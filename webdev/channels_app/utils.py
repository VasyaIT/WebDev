from django.db import IntegrityError


def pre_channel_save(channel):
    try:
        channel.save()
    except IntegrityError:
        channel.slug += '_'
        pre_channel_save(channel)
