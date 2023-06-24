from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db import IntegrityError, transaction
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers
from rest_framework.views import APIView

from api.users.services import email_confirm
from users.models import Account, Subscribe


User = get_user_model()


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['is_premium', 'avatar', 'about', 'rating']


class Friend(serializers.ModelSerializer):
    class Meta:
        model = Subscribe
        exclude = ['created_at']


class UserSerializer(serializers.ModelSerializer):
    account = AccountSerializer()
    count_subscribers = serializers.SerializerMethodField()
    friends = serializers.SerializerMethodField()
    friend_req = serializers.SerializerMethodField()
    friending_req = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['username', 'account', 'count_subscribers',
                  'friends', 'friend_req', 'friending_req']

    def get_count_subscribers(self, obj: User) -> int:
        return obj.subscribers.count()

    def get_friends(self, obj: User) -> list[str, ...]:
        user_friends = [u.user_to.username
                        for u in obj.friending.filter(is_friend=True).
                        select_related('user_from', 'user_to')]
        return user_friends

    def get_friend_req(self, obj: User) -> list[str, ...]:
        user_friends_req = [u.user_from.username
                            for u in obj.friends.filter(is_friend=False).
                            select_related('user_from', 'user_to')]
        return user_friends_req

    def get_friending_req(self, obj: User) -> list[str, ...]:
        user_friending_req = [u.user_to.username
                              for u in obj.friending.filter(is_friend=False).
                              select_related('user_from', 'user_to')]
        return user_friending_req


class AccountUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['about', 'avatar']

    def update(self, instance, validated_data) -> Account:
        if not validated_data.get('avatar'):
            instance.avatar.delete()
            return instance
        else:
            return super().update(instance, validated_data)


class CustomUserCreateSerializer(UserCreateSerializer):
    def create(self, validated_data):
        email_confirm(validated_data, self.context.get('request'))
        del validated_data['ub64']
        del validated_data['token']
        user = User.objects.create(**validated_data)
        user.delete()
        return user
