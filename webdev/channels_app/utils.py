from random import choice, randint
import string
from time import time

from django.db.models import QuerySet, Q
from django.utils.text import slugify


def save_channel_form(form, request) -> None:
    """Saving form if it is valid"""
    channel = form.save(commit=False)
    channel.author = request.user
    channel.save()
    form.save_m2m()


def generate_slug(channel_name) -> str:
    """Generating channel slug"""
    random_number = randint(5, 15)
    slug_string = string.ascii_lowercase
    rand_string = ''.join(choice(slug_string) for _ in range(random_number))
    channel_slug = f'{slugify(channel_name)}-{str(int(time()))}_{rand_string}'
    return channel_slug


def get_filtered_channels(form, tags_form, channels_list) -> QuerySet:
    """Getting a filtered channel request"""
    query = form.cleaned_data['query']
    result = (Q
              (name__icontains=query) | Q(tags__name__icontains=query) | Q
              (author__username__icontains=query) | Q(description__icontains=query)
              )
    tags_queryset = tags_form.qs
    channels_queryset = channels_list.filter(result).distinct()
    channels_list = tags_queryset.filter(result).distinct()
    if len(channels_list) == 0:
        channels_list = channels_queryset
    return channels_list
