import redis
import stripe
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

from webdev.logger_config import logger
from payments.decorators import not_is_premium
from payments.utils import get_session_data, generate_success_redirect_url

stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.api_version = settings.STRIPE_API_VERSION


r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=2)


@require_POST
@login_required
@not_is_premium
def process(request):
    user = request.user

    if request.method == 'POST':
        red = generate_success_redirect_url(user)
        r.set(f'redirect-{user}', red, 600)
        r.close()
        session = get_session_data(request, red, 'payment_completed', 'index')
        logger.info(f'{user} starts to create a premium account'
                    f' with redirect key: {red}')
        return redirect(session.url, code=303)


@login_required
def completed(request):
    user = request.user

    if (
        'success' in request.GET
        and f"b'{str(request.GET['success'])}'" == str(r.get(f'redirect-{user}'))
    ):
        r.delete(f'redirect-{user}')
        r.close()
        logger.success(f'{user} completed pay premium account and redirect key deleted')
        return render(request, 'payments/completed.html')
    return redirect('index')
