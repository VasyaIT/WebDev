from django.urls import path, re_path
from django.contrib.auth import views as view

from . import views
from .forms import LogInForm, CustomPasswordChangeForm

urlpatterns = [
    path('signup/', views.SignUp.as_view(redirect_authenticated_user=True), name='signup'),
    path(
        'login/',
        view.LoginView.as_view(
            template_name='users/login.html',
            form_class=LogInForm,
            redirect_authenticated_user=True
        ),
        name='login'
    ),
    path('logout/', view.LogoutView.as_view(), name='logout'),
    path(
        'password_change/',
        views.MyPasswordChangeView.as_view(
            form_class=CustomPasswordChangeForm,
            template_name='users/password_change_form.html'
        ),
        name='password_change'
    ),
    path(
        'password_reset/',
        view.PasswordResetView.as_view(
            template_name='users/password_reset_subject.html'
        ),
        name='password_reset'
    ),
    path(
        'password_reset_done/',
        view.PasswordResetDoneView.as_view(
            template_name='users/password_reset_done.html'
        ),
        name='password_reset_done'
    ),
    path(
        'password_reset_confirm/',
        view.PasswordResetConfirmView.as_view(
            template_name='users/password_reset_confirm.html'
        ),
        name='password_reset_confirm'
    ),
    path(
        'password_reset_complete/',
        view.PasswordResetCompleteView.as_view(
            template_name='users/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),
]
