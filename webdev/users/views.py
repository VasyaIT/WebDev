from django.contrib.auth.views import PasswordChangeView
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, login, update_session_auth_hash
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import SignUpForm

User = get_user_model()


class SignUp(CreateView):
    redirect_authenticated_user = False

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

    form_class = SignUpForm
    template_name = 'users/signup.html'
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('index')


class MyPasswordChangeView(PasswordChangeView):
    success_url = None

    def get_context_data(self, **kwargs):
        password_changed = False
        context = super().get_context_data(**kwargs)
        context.update(
            {"title": self.title, "subtitle": None, **(self.extra_context or {}), 'password_changed': password_changed}
        )
        return context

    # def form_valid(self, form):
    #     password_changed = False
    #     form.save()
    #     update_session_auth_hash(self.request, form.user)
    #     password_changed = True
    #     return super().form_valid(form)
