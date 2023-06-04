from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404

from webdev.logger_config import logger

User = get_user_model()


@shared_task
def user_save_and_send_mail(user_email_form, user_id):
    user = get_object_or_404(User.objects.select_related('account'),
                             id=user_id)
    user.account.is_premium = True
    user.account.save()

    logger.success(f'{user} has issued a premium account!')

    send_mail(
        'Premium account received',
        'Congratulations!\nYou have purchased a premium account received!\n'
        'With respect,\n'
        'WebDev',
        settings.EMAIL_HOST_USER,
        [user_email_form, user.email],
    )

    logger.info(f'Email sent succeeded to {user}')
