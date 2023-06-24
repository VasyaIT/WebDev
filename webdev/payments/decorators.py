from django.shortcuts import redirect

from webdev.logger_config import logger


def not_is_premium(func):
    def wrapper(self, request, *args, **kwargs):
        if request.user.account.is_premium:
            logger.info(f'Premium user: {request.user} tried to navigate "/payment/process"')
            return redirect('index')
        return func(request, *args, **kwargs)
    return wrapper
