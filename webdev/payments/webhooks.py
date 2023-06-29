import json

import stripe
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .tasks import user_save_and_send_mail
from webdev.logger_config import logger

User = get_user_model()


@csrf_exempt
def stripe_webhook(request) -> HttpResponse:
    payload = request.body
    # sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Event.construct_from(json.loads(payload), settings.STRIPE_WEBHOOK_SECRET)
    # try:
    #     event = stripe.Webhook.construct_event(
    #         payload,
    #         sig_header,
    #         settings.STRIPE_WEBHOOK_SECRET)
    except ValueError as v:
        logger.error(v)
        return HttpResponse(status=400)

    if event.type == 'checkout.session.completed':
        session = event.data.object
        if session.mode == 'payment' and session.payment_status == 'paid':
            user_save_and_send_mail.delay(session.customer_details.email,
                                          session.client_reference_id)
    return HttpResponse(status=200)
