from api.channels.serializers import ChannelSerializer
from channels_app.models import Channel


class ListCreateMixin:
    queryset = (
        Channel.online.select_related('author')
        .prefetch_related('current_users', 'tags')
    )
    serializer_class = ChannelSerializer
