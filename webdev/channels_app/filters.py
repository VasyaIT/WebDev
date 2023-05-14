from django_filters import FilterSet
from .models import Channel


class ChannelFilter(FilterSet):
    class Meta:
        model = Channel
        fields = ['tags']
