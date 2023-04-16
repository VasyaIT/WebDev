from django.urls import path
from . import views
from django.contrib.auth import views as view

urlpatterns = [
    path('signup/', views.SignUp.as_view(redirect_authenticated_user=True), name='signup'),
    path(
        'login/', view.LoginView.as_view(
            template_name='users/login.html',
            redirect_authenticated_user=True), name='login'
    ),
    path('logout/', view.LogoutView.as_view(template_name='users/logout.html'), name='logout')
]
