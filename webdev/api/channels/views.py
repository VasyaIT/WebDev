from django.db import IntegrityError
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from channels_app.filters import ChannelFilter
from channels_app.models import Channel, Tag
from channels_app.utils import get_filtered_channels
from .mixins import ListCreateMixin
from .serializers import ChannelRetrieveSerializer, ChannelUpdateSerializer


class ChannelListAPI(ListCreateMixin, generics.ListAPIView):
    @method_decorator(cache_page(2))
    def get(self, request, *args, **kwargs):
        tags_qs = ChannelFilter(request.GET, queryset=Channel.online.select_related('author')).qs

        if 'query' in request.GET or 'tags' in request.GET:
            self.queryset = get_filtered_channels(
                request.GET.get('query', ''), tags_qs, self.queryset
            ).prefetch_related('tags', 'current_users')

        tag_slug = kwargs.get('tag_slug')
        if tag_slug:
            self.queryset = self.queryset.filter(tags__slug__in=[tag_slug])

        return super().get(request, *args, **kwargs)


class ChannelCreateAPI(ListCreateMixin, generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs) -> HttpResponse:
        channel = Channel.objects.filter(author=request.user)
        if channel.exists():
            return Response({'error': 'You can only have one created channel'})
        try:
            return super().post(request, *args, **kwargs)
        except IntegrityError:
            return Response({'error': 'Unknown error. Try again'})
        except (Tag.DoesNotExist, AttributeError):
            return Response({'error': 'There is no such tag'})


class ChannelRetrieveAPI(generics.RetrieveAPIView):
    queryset = (Channel.objects.select_related('author')
                .prefetch_related('current_users', 'tags', 'messages__user'))
    serializer_class = ChannelRetrieveSerializer
    lookup_field = 'slug'
    permission_classes = (IsAuthenticated,)


class ChannelDeleteAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def delete(self, request) -> HttpResponse:
        channel = Channel.objects.filter(author=request.user)
        if channel.exists():
            instance = channel[0]
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


class ChannelUpdateAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request) -> HttpResponse:
        self.channel = Channel.objects.filter(author=request.user)
        if not self.channel.exists():
            return Response(status=status.HTTP_403_FORBIDDEN)
        try:
            return self.update(request)
        except IntegrityError:
            return Response({'error': 'Unknown error. Try again'})

    def update(self, request) -> HttpResponse:
        instance = self.channel[0]
        previous_tags = instance.tags.all()
        serializer = ChannelUpdateSerializer(instance, request.data)
        serializer.is_valid(raise_exception=True)
        new_tags = serializer.validated_data.get('tags')
        if new_tags:
            new_tags_obj = []
            for tag in new_tags:
                try:
                    tag_obj = Tag.objects.get(name=tag['name'])
                    print(tag_obj)
                except Tag.DoesNotExist:
                    print('ex')
                    return Response({'error': 'There is no such tag'})
                new_tags_obj.append(tag_obj)
            instance.tags.set(new_tags_obj)
        else:
            instance.tags.set(previous_tags)
        serializer.save()
        return Response(serializer.data)
