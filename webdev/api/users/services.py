import redis
from django.conf import settings

from users.utils import generate_ub64, generate_token, generate_email_message
from users.tasks import confirm_email_send


def email_confirm(data: dict[str, ...], request) -> None:
    """Sending email with confirm token and encode username"""
    r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=2)

    ub64 = generate_ub64(data['username'])
    token = generate_token()

    data['ub64'] = ub64
    data['token'] = token

    message = generate_email_message(data['username'], request, ub64, token, 'api_profile_edit')

    confirm_email_send.delay(message, data['email'])

    key = f'token-{data["username"]}'
    r.hmset(key, data)
    r.expire(key, 300)
    r.close()
