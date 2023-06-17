from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from channels_app.models import Channel, Tag
from .mixins import ListCreateMixin
from .serializers import ChannelSerializer, ChannelRetrieveSerializer, ChannelUpdateSerializer


class ChannelListAPI(ListCreateMixin, generics.ListAPIView):
    def get(self, request, *args, **kwargs):
        tag_slug = kwargs.get('tag_slug')
        if tag_slug:
            self.queryset = (
                Channel.online.filter(tags__slug__in=[tag_slug])
                .select_related('author')
                .prefetch_related('current_users', 'tags')
                .order_by('-online')
            )
        return super().get(request, *args, **kwargs)


class ChannelCreateAPI(ListCreateMixin, LoginRequiredMixin, generics.CreateAPIView):
    def post(self, request, *args, **kwargs):
        channel = Channel.objects.filter(author=request.user)
        if channel.exists():
            return Response({'error': 'You can only have one created channel'})
        try:
            return super().post(request, *args, **kwargs)
        except IntegrityError:
            return Response({'error': 'Unknown error. Try again'})
        except (Tag.DoesNotExist, AttributeError):
            return Response({'error': 'There is no such tag'})


class ChannelRetrieveAPI(generics.RetrieveAPIView, LoginRequiredMixin):
    queryset = (Channel.objects.select_related('author')
                .prefetch_related('current_users', 'tags', 'messages__user'))
    serializer_class = ChannelRetrieveSerializer
    lookup_field = 'slug'


class ChannelDeleteAPI(APIView, LoginRequiredMixin):
    def delete(self, request):
        channel = Channel.objects.filter(author=request.user)
        if channel.exists():
            instance = channel[0]
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


class ChannelUpdateAPI(APIView, LoginRequiredMixin):
    def put(self, request):
        self.channel = Channel.objects.filter(author=request.user)
        if not self.channel.exists():
            return Response(status=status.HTTP_403_FORBIDDEN)
        try:
            return self.update(request)
        except IntegrityError:
            return Response({'error': 'Unknown error. Try again'})

    def update(self, request):
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
                except Tag.DoesNotExist:
                    return Response({'error': 'There is no such tag'})
                new_tags_obj.append(tag_obj)
            instance.tags.set(new_tags_obj)
        else:
            instance.tags.set(previous_tags)
        serializer.save()
        return Response(serializer.data)
