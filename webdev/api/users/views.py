import redis
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.utils.http import urlsafe_base64_decode
from django.views.decorators.cache import cache_page
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_405_METHOD_NOT_ALLOWED
from rest_framework.utils.serializer_helpers import ReturnDict
from rest_framework.views import APIView

from webdev.logger_config import logger
from api.users.serializers import UserSerializer, AccountUpdateSerializer
from channels_app.models import Channel
from users.models import Account
from users.utils import user_action

User = get_user_model()


class UserRetrieveAPI(RetrieveAPIView):
    queryset = User.objects.select_related('account')
    serializer_class = UserSerializer
    lookup_field = 'username'

    @method_decorator(cache_page(60))
    def retrieve(self, request, *args, **kwargs) -> HttpResponse:
        self.user = kwargs['username']
        self.request_user = request.user.username
        instance = self.get_object()
        self.serializer = self.get_serializer(instance)
        sd = self.new_serializer()
        return Response(sd)

    def new_serializer(self) -> ReturnDict[str, ...]:
        sd = self.serializer.data
        sd['has_channel'] = False
        if self.user is self.request_user:
            sd['count_friend_req'] = len(sd['friend_req'])
            sd['count_friending_req'] = len(sd['friending_req'])
        else:
            del sd['friend_req']
            del sd['friending_req']
        if Channel.objects.filter(author__username=self.user).exists():
            sd['has_channel'] = True

        sd['is_premium'] = sd['account']['is_premium']
        sd['avatar'] = sd['account']['avatar']
        sd['about'] = sd['account']['about']
        sd['rating'] = sd['account']['rating']
        sd['count_friends'] = len(sd['friends'])
        del sd['account']

        return sd


class AccountUpdateAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request) -> HttpResponse:
        queryset = Account.objects.get(user=request.user)
        serializer = AccountUpdateSerializer(queryset)
        return Response(serializer.data)

    def put(self, request) -> HttpResponse:
        queryset = Account.objects.get(user=request.user)
        serializer = AccountUpdateSerializer(queryset, request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class UserContact(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs) -> HttpResponse:
        user_id = request.data.get('user_id')
        action = request.data.get('action')
        if user_id and action and action in settings.ACTIONS:
            if str(request.user.id) == str(user_id):
                return Response(status=HTTP_405_METHOD_NOT_ALLOWED)
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response(status=HTTP_405_METHOD_NOT_ALLOWED)
            user_action(request.user, user, action)
            return Response({action: f'{request.user} with {user}'})
        else:
            return Response(status=HTTP_405_METHOD_NOT_ALLOWED)


class UserSignupConfirmAPI(APIView):
    def get(self, request, *args, **kwargs):
        r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=2)
        u64 = kwargs.get('ub64')
        token = kwargs.get('token')

        try:
            ub64 = urlsafe_base64_decode(u64).decode('utf-8')
        except (UnicodeDecodeError, ValueError):
            return Response({'error': 'This link is invalid'})

        redis_data = r.hgetall(f'token-{ub64}')
        form_data = {key.decode('utf-8'): value.decode('utf-8') for key, value in
                     redis_data.items()}
        if form_data:
            if form_data['token'] == token:
                user = User.objects.create_user(
                    username=form_data['username'],
                    email=form_data['email'],
                    password=form_data['password']
                )
                Account.objects.create(user=user)

                logger.info(f'{user} registered success')

                r.delete(f'token-{ub64}')
                r.close()
                return Response({'success': 'Email Confirm'})
        return Response({'error': 'This link is invalid'})
