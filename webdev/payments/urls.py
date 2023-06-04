from django.urls import path
from . import views
from . import webhooks

urlpatterns = [
    path('process/', views.process, name='payment_process'),
    path('complete/', views.completed, name='payment_completed'),
    path('webhook/', webhooks.stripe_webhook, name='stripe_webhook')
]
