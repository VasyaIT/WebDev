import hashlib
import string
from random import randint, choice

from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.urls import reverse_lazy

from users.models import Friend, Subscribe
from .tasks import confirm_email_send
from webdev.logger_config import logger


User = get_user_model()


def user_action(request, user_id, action) -> None:
    """Action from POST request. The logic of subscriptions and adding friends"""
    user = User.objects.get(id=user_id)
    qs = Friend.objects.filter(user_from=request.user, user_to=user)
    qs_rev = Friend.objects.filter(user_from=user, user_to=request.user)
    if action == 'Subscribe':
        Subscribe.objects.get_or_create(
            user_from=request.user,
            user_to=user)
        logger.info(f'{request.user} subscribed to {user}')
    elif action == 'Unsubscribe':
        Subscribe.objects.filter(user_from=request.user,
                                 user_to=user).delete()
        logger.info(f'{request.user} unsubscribed from {user}')
    elif action == 'Add to Friends':
        qs.get_or_create(user_from=request.user, user_to=user)
    elif action == 'Accept the request' and qs_rev.exists():
        Friend.objects.create(user_from=request.user, user_to=user)
        logger.info(f'Created a new friendship with {request.user} and {user}')
    elif action == 'Remove from Friends' and qs.exists() and qs_rev.exists():
        qs.delete() and qs_rev.delete()
        logger.info(f'{request.user} deleted from friends {user}')
    elif action == 'Cancel the request' and qs.exists() and not qs_rev.exists():
        qs.delete()
    elif action == 'Reject request' and qs_rev.exists() and not qs.exists():
        qs_rev.delete()


def email_confirm(form, request):
    """Sending email with confirm token"""
    user = form.save(commit=False)

    token = generate_token(user)
    message = generate_email_message(user, request, token)

    confirm_email_send.delay(message, user.email)

    request.session['INTERNAL_RESET_SESSION_TOKEN'] = token
    request.session['USER'] = form.cleaned_data
    return render(request, 'users/send_confirm_mail.html')


def generate_token(user) -> str:
    """Generate random token with hash username"""
    random_number = randint(20, 30)
    all_letters = string.ascii_lowercase
    hsh = hashlib.sha1(user.username.encode())
    token = f"{''.join(choice(all_letters) for _ in range(random_number))}_{hsh.hexdigest()}"
    return token


def generate_email_message(user, request, token) -> str:
    """Message is composed to be sent to the mail"""
    url = request.build_absolute_uri(reverse_lazy('signup'))

    message = f"""
    Dear {user}, Thank You for using our website.
    Email confirmation link:
    {url}{token}/
    it wasn't you, just ignore this message."""

    return message
