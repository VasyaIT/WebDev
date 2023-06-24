import string
from random import randint, choice

import redis
from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from users.models import Friend, Subscribe
from .tasks import confirm_email_send
from webdev.logger_config import logger


User = get_user_model()


def user_action(request_user: User, user: User, action: str) -> None:
    """Action from POST request. The logic of subscriptions and adding friends"""
    qs = Friend.objects.filter(user_from=request_user, user_to=user)
    qs_rev = Friend.objects.filter(user_from=user, user_to=request_user)
    if action == 'Subscribe':
        Subscribe.objects.get_or_create(
            user_from=request_user,
            user_to=user)
        logger.info(f'{request_user} subscribed to {user}')
    elif action == 'Unsubscribe':
        Subscribe.objects.filter(user_from=request_user,
                                 user_to=user).delete()
        logger.info(f'{request_user} unsubscribed from {user}')
    elif action == 'Add to Friends':
        qs.get_or_create(user_from=request_user, user_to=user)
    elif action == 'Accept the request' and qs_rev.exists():
        Friend.objects.create(user_from=request_user, user_to=user)
        logger.info(f'Created a new friendship with {request_user} and {user}')
    elif action == 'Remove from Friends' and qs.exists() and qs_rev.exists():
        qs.delete() and qs_rev.delete()
        logger.info(f'{request_user} deleted from friends {user}')
    elif action == 'Cancel the request' and qs.exists() and not qs_rev.exists():
        qs.delete()
    elif action == 'Reject request' and qs_rev.exists() and not qs.exists():
        qs_rev.delete()


def email_confirm(data: dict[str, ...], request):
    """Sending email with confirm token and encode username"""
    r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=2)

    ub64 = generate_ub64(data['username'])
    token = generate_token()

    data['ub64'] = ub64
    data['token'] = token

    message = generate_email_message(data['username'], request, ub64, token, 'signup')

    confirm_email_send.delay(message, data['email'])

    key = f'token-{data["username"]}'
    r.hmset(key, data)
    r.expire(key, 300)
    r.close()
    return render(request, 'users/send_confirm_mail.html')


def generate_ub64(username) -> str:
    """Encoding username for email link"""
    ub64 = urlsafe_base64_encode(force_bytes(username))
    return ub64


def generate_token() -> str:
    """Generate random token for email link"""
    random_number = randint(20, 30)
    all_letters = string.ascii_lowercase
    token = ''.join(choice(all_letters) for _ in range(random_number))
    return token


def generate_email_message(username, request, ub64, token, url_name) -> str:
    """Message is composed to be sent to the mail"""
    url = request.build_absolute_uri(reverse_lazy(url_name))

    message = f"""
    Dear {username}, Thank You for using our website.
    Email confirmation link:
    {url}{ub64}/{token}
    it wasn't you, just ignore this message."""

    return message
