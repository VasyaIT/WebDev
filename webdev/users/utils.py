from django.contrib.auth import get_user_model

from users.models import Friend, Subscribe
from webdev.logger_config import logger


User = get_user_model()


def user_action(request, user_id, action) -> None:
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
