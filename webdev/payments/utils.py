import string
from random import choice

from django.conf import settings
from stripe.api_resources.checkout import Session
from django.urls import reverse


def get_session_data(request, red: str, success_url_name: str, cancel_url_name: str) -> Session:
    """
    Create stripe session data with success and cancel urls
    and user_id
    Key line_items consists of payment data
    """
    user = request.user
    success_url = f"{request.build_absolute_uri(reverse(success_url_name))}?success={red}"
    cancel_url = request.build_absolute_uri(reverse(cancel_url_name))

    session_data = {
        'mode': 'payment',
        'client_reference_id': user.id,
        'success_url': success_url,
        'cancel_url': cancel_url,
        'line_items': [],
    }

    session_data['line_items'].append({
        'price_data': {
            'unit_amount': settings.PREMIUM_ACCOUNT_PRICE,
            'currency': 'usd',
            'product_data': {
                'name': 'Premium account'
            },
        },
        'quantity': 1,
    })

    session = Session.create(**session_data)
    return session


def generate_success_redirect_url(user: str) -> str:
    """Generate random string of 15 letters and username"""
    all_letters = string.ascii_lowercase
    redirect_string = ''.join(choice(all_letters) for _ in range(15)) + '-' + str(user)
    return redirect_string
