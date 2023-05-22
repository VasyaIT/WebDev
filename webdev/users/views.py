from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView, PasswordResetConfirmView, \
        INTERNAL_RESET_SESSION_TOKEN, PasswordResetView
from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model, login, update_session_auth_hash
from django.urls import reverse_lazy
from django.views.decorators import debug, cache, csrf
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.views.generic import CreateView
from django.core.exceptions import ImproperlyConfigured

from .models import Account, Subscribe
from .forms import SignUpForm, CustomPasswordChangeForm, CustomPasswordResetForm, \
        CustomSetPasswordForm

User = get_user_model()


def profile(request, username):
    """Rendering user profile"""
    user = get_object_or_404(User.objects.select_related('account'),
                             username=username,
                             is_active=True)
    context = {
        'user': user,
    }
    return render(request, 'users/profile.html', context)


@require_POST
@login_required
def user_subscribe(request):
    user_id = request.POST.get('id')
    action = request.POST.get('action')
    if user_id and action:
        if user_id == str(request.user.id):
            return JsonResponse({'status': 'error'})
        try:
            user = User.objects.get(id=user_id)
            if action == 'subscribe':
                Subscribe.objects.get_or_create(
                    user_from=request.user,
                    user_to=user)
            else:
                Subscribe.objects.filter(user_from=request.user,
                                         user_to=user).delete()
            return JsonResponse({'status': 'ok'})
        except User.DoesNotExist:
            return JsonResponse({'status': 'error'})
    return JsonResponse({'status': 'error'})


class SignUp(CreateView):
    redirect_authenticated_user = False
    form_class = SignUpForm
    template_name = 'users/signup.html'
    success_url = reverse_lazy('index')

    def dispatch(self, request, *args, **kwargs):
        if self.redirect_authenticated_user and self.request.user.is_authenticated:
            redirect_to = '/'
            if redirect_to == self.request.path:
                raise ValueError(
                    "Redirection loop for authenticated user detected. Check that "
                    "your LOGIN_REDIRECT_URL doesn't point to a login page."
                )
            return HttpResponseRedirect(redirect_to)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save()
        Account.objects.create(user=user)
        login(self.request, user, backend=settings.AUTHENTICATION_BACKENDS[0])
        return redirect('index')


class MyPasswordChangeView(PasswordChangeView):
    success_url = None
    form_class = CustomPasswordChangeForm
    template_name = 'users/password_change_form.html'

    def form_valid(self, form):
        form_valid = True
        form.save()
        update_session_auth_hash(self.request, form.user)
        return render(self.request, 'users/password_change_form.html', {'form_valid': form_valid})


class MyPasswordResetConfirmView(PasswordResetConfirmView):
    success_url = None
    form_class = CustomSetPasswordForm
    template_name = 'users/password_reset_confirm.html'

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

    def form_valid(self, form):
        form_valid = True
        user = form.save()
        del self.request.session[INTERNAL_RESET_SESSION_TOKEN]
        if self.post_reset_login:
            login(self.request, user, self.post_reset_login_backend)
        return render(self.request, 'users/password_reset_confirm.html', {'form_valid': form_valid})


class MyPasswordResetView(PasswordResetView):
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
        return render(self.request, 'users/password_reset_form.html', {'form_valid': form_valid})
