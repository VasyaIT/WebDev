from django.urls import path
from django.contrib.auth import views as view

from . import views
from .forms import LogInForm


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
    path('password-change/', views.MyPasswordChangeView.as_view(), name='password_change'),
    path('password-reset/', views.MyPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/<uidb64>/<token>/',
         views.MyPasswordResetConfirmView.as_view(),
         name='password_reset_confirm'
         ),
]
