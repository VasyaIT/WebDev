from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from rest_framework.generics import RetrieveAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_405_METHOD_NOT_ALLOWED
from rest_framework.utils.serializer_helpers import ReturnDict
from rest_framework.views import APIView

from api.users.serializers import UserSerializer, AccountUpdateSerializer
from channels_app.models import Channel
from users.models import Account
from users.utils import user_action

User = get_user_model()


class UserRetrieveAPI(RetrieveAPIView):
    queryset = User.objects.select_related('account')
    serializer_class = UserSerializer
    lookup_field = 'username'

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


class AccountUpdateAPI(LoginRequiredMixin, APIView):
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


class UserContact(LoginRequiredMixin, APIView):
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
