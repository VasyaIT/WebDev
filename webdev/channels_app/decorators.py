from django.http import Http404

from .models import Channel


def have_channel_required(func):
    """Raise 404 if user doesn't have a channel"""
    def wrapper(request, *args):
        user = request.user
        if not Channel.objects.filter(author=user).exists():
            raise Http404
        return func(request, *args)
    return wrapper
