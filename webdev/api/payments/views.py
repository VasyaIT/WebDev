import redis
from django.conf import settings
from django.shortcuts import redirect
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from payments.utils import get_session_data, generate_success_redirect_url
from webdev.logger_config import logger


r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=2)


class Process(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user = request.user

        if request.user.account.is_premium:
            return Response({'error': 'premium account already'})
        red = generate_success_redirect_url(user)
        r.set(f'redirect-{user}', red, 600)
        r.close()
        session = get_session_data(request, red, 'api_complete', 'api_channels_list')
        logger.info(f'{user} starts to create a premium account'
                    f' with redirect key: {red}')
        return redirect(session.url, code=303)


class Complete(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user

        if (
                'success' in request.GET
                and f"b'{str(request.GET['success'])}'" == str(r.get(f'redirect-{user}'))
        ):
            r.delete(f'redirect-{user}')
            r.close()
            logger.success(f'{user} completed pay premium account and redirect key deleted')
            return Response({'success': 'completed pay premium'})
        return redirect('api_channels_list')
