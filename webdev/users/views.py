import redis
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView, PasswordResetConfirmView, \
        INTERNAL_RESET_SESSION_TOKEN, PasswordResetView
from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model, login, update_session_auth_hash
from django.urls import reverse_lazy
from django.views.decorators import debug, cache, csrf
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.views.generic import CreateView
from django.core.exceptions import ImproperlyConfigured
from django.utils.http import urlsafe_base64_decode

from channels_app.models import Channel
from .models import Account
from .forms import SignUpForm, CustomPasswordChangeForm, CustomPasswordResetForm, \
    CustomSetPasswordForm, AccountEditForm
from .utils import user_action, email_confirm
from webdev.logger_config import logger

User = get_user_model()


def profile(request, username: str) -> HttpResponse:
    """Rendering user profile"""
    user = get_object_or_404(User.objects.select_related('account', 'channels'),
                             username=username,
                             is_active=True)
    user_friends = [u.user_to
                    for u in user.friending.filter(is_friend=True).
                    select_related('user_from', 'user_to')]
    user_friends_req = [u.user_from
                        for u in user.friends.filter(is_friend=False).
                        select_related('user_from', 'user_to')]
    user_friending_req = [u.user_to
                          for u in user.friending.filter(is_friend=False).
                          select_related('user_from', 'user_to')]

    have_channel = False
    channel = Channel.objects.filter(author=user)
    if channel.exists():
        have_channel = True

    context = {
        'user': user,
        'user_friends': user_friends,
        'user_friends_req': user_friends_req,
        'user_friending_req': user_friending_req,
        'channel': channel,
        'have_channel': have_channel,
    }
    return render(request, 'users/profile.html', context)


@login_required
def profile_edit(request) -> HttpResponse:
    """Editing the user profile"""
    if request.method == 'POST':
        form = AccountEditForm(request.POST, request.FILES, instance=request.user.account)
        if request.POST.get('action') == 'delete_avatar':
            account = form.save(commit=False)
            account.avatar = None
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully')
    else:
        form = AccountEditForm(instance=request.user.account)
    return render(request, 'users/profile_edit.html', {'form': form})


@require_POST
@login_required
def user_contact(request) -> JsonResponse:
    """Subscribing or Unsubscribing on user"""
    user_id = request.POST.get('id')
    action = request.POST.get('action')
    if user_id and action and action in settings.ACTIONS:
        if user_id == str(request.user.id):
            return JsonResponse({'status': 'error'})
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            logger.error('Was received non-existing user in POST request')
            return JsonResponse({'status': 'error'})
        user_action(request.user, user, action)
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'})


class SignUp(CreateView):
    """Register and auto log in. Create an account"""
    redirect_authenticated_user = False
    form_class = SignUpForm
    template_name = 'users/signup.html'
    success_url = reverse_lazy('index')

    def dispatch(self, request, *args, **kwargs):
        if self.redirect_authenticated_user and self.request.user.is_authenticated:
            redirect_to = '/'
            if redirect_to == self.request.path:
                raise ValueError(
                    "Redirection loop for signup user detected. Check that "
                    "`redirect_to` doesn't point to a signup page."
                )
            return HttpResponseRedirect(redirect_to)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        return email_confirm(form.cleaned_data, self.request)


def signup_confirm(request, ub64, token):
    r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=2)
    valid = False

    try:
        ub64 = urlsafe_base64_decode(ub64).decode('utf-8')
    except (UnicodeDecodeError, ValueError):
        valid = False

    redis_data = r.hgetall(f'token-{ub64}')
    form_data = {key.decode('utf-8'): value.decode('utf-8') for key, value in redis_data.items()}
    if form_data:
        if form_data['token'] == token:
            user = User.objects.create_user(
                username=form_data['username'],
                email=form_data['email'],
                password=form_data['password1']
            )
            Account.objects.create(user=user)

            login(request, user, backend=settings.AUTHENTICATION_BACKENDS[0])
            logger.info(f'{user} registered success')
            valid = True

            r.delete(f'token-{ub64}')
            r.close()
    return render(request, 'users/email_confirm.html', {'valid': valid})


class MyPasswordChangeView(PasswordChangeView):
    """Password change"""
    success_url = None
    form_class = CustomPasswordChangeForm
    template_name = 'users/password_change_form.html'

    def form_valid(self, form):
        form_valid = True
        form.save()
        update_session_auth_hash(self.request, form.user)
        logger.info(f'{form.user} changed password successfully')
        return render(self.request, 'users/password_change_form.html', {'form_valid': form_valid})


class MyPasswordResetView(PasswordResetView):
    """Password reset form"""
    form_class = CustomPasswordResetForm
    success_url = None
    template_name = "users/password_reset_form.html"

    @method_decorator(csrf.csrf_protect)
    def dispatch(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('index')
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        form_valid = True
        opts = {
            "use_https": self.request.is_secure(),
            "token_generator": self.token_generator,
            "from_email": self.from_email,
            "email_template_name": self.email_template_name,
            "subject_template_name": self.subject_template_name,
            "request": self.request,
            "html_email_template_name": self.html_email_template_name,
            "extra_email_context": self.extra_email_context,
        }
        form.save(**opts)
        logger.info(f'Some user made a password reset request at email '
                    f'{form.cleaned_data["email"]}')
        return render(self.request, 'users/password_reset_form.html', {'form_valid': form_valid})


class MyPasswordResetConfirmView(PasswordResetConfirmView):
    """Set new password"""
    success_url = reverse_lazy(settings.LOGIN_REDIRECT_URL)
    form_class = CustomSetPasswordForm
    template_name = 'users/password_reset_confirm.html'
    post_reset_login = True
    post_reset_login_backend = settings.AUTHENTICATION_BACKENDS[0]

    @method_decorator(debug.sensitive_post_parameters())
    @method_decorator(cache.never_cache)
    def dispatch(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('index')
        if "uidb64" not in kwargs or "token" not in kwargs:
            raise ImproperlyConfigured(
                "The URL path must contain 'uidb64' and 'token' parameters."
            )

        self.validlink = False
        self.user = self.get_user(kwargs["uidb64"])

        if self.user is not None:
            token = kwargs["token"]
            if token == self.reset_url_token:
                session_token = self.request.session.get(INTERNAL_RESET_SESSION_TOKEN)
                if self.token_generator.check_token(self.user, session_token):
                    self.validlink = True
                    return super().dispatch(*args, **kwargs)
            else:
                if self.token_generator.check_token(self.user, token):
                    self.request.session[INTERNAL_RESET_SESSION_TOKEN] = token
                    redirect_url = self.request.path.replace(
                        token, self.reset_url_token
                    )
                    return HttpResponseRedirect(redirect_url)

        return self.render_to_response(self.get_context_data())
