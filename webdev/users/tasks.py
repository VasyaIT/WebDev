from celery import shared_task
from django.core.mail import send_mail


@shared_task
def confirm_email_send(message, user_email):
    send_mail(
        'Email confirm on WebDev',
        message,
        'johnwilli6bg@gmail.com',
        [user_email],
    )
