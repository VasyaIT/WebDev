from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import IntegrityError
from django.http import Http404

from django.shortcuts import render, redirect, get_object_or_404

from .forms import ChannelForm
from .models import Channel, Message, Tag

from .utils import save_channel_form

User = get_user_model()


def index(request, tag_slug=None):
    channels_list = Channel.objects.select_related('author').prefetch_related('current_users', 'tags')

    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        channels_list = channels_list.filter(tags__in=[tag]).select_related('author')\
            .prefetch_related('tags', 'current_users')

    paginator = Paginator(channels_list, 3)
    page_number = request.GET.get('page', 1)

    try:
        channels = paginator.page(page_number)
    except EmptyPage:
        channels = paginator.page(1)
    except PageNotAnInteger:
        raise Http404

    context = {
        'channels': channels,
        'tag': tag,
    }
    return render(request, 'channels/index.html', context)


@login_required
def detail_channel(request, slug):
    channels = get_object_or_404(Channel.objects.select_related('author'), slug=slug)
    messages = Message.objects.select_related('channel', 'user').filter(channel=channels)[:50]

    context = {
        'channels': channels,
        'messages': messages,
    }
    return render(request, 'channels/detail_channel.html', context)


@login_required
def create_channel(request):
    error = ''
    form = ChannelForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            try:
                save_channel_form(form, request)
                return redirect('index')
            except IntegrityError:
                error = 'Unknown error. Try again'
        else:
            error = 'Incorrect form'

    form = ChannelForm()
    context = {
        'form': form,
        'error': error,
    }

    return render(request, 'channels/create_channel.html', context)
