from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db import IntegrityError

from django.shortcuts import render, redirect

from .forms import ChannelForm
from .models import Channel, Message
from django.template.defaultfilters import slugify

from .utils import save_channel_form

User = get_user_model()


def index(request):
    channels = Channel.objects.select_related('author').prefetch_related('current_users', 'tags').order_by('-id')
    context = {
        'channels': channels,
    }
    return render(request, 'channels/index.html', context)


@login_required(login_url='/auth/login/')
def detail_channel(request, slug):
    channels = Channel.objects.select_related('author').get(slug=slug)
    messages = Message.objects.select_related('channel', 'user').filter(channel=channels).order_by('id')[0:25]

    context = {
        'channels': channels,
        'messages': messages
    }
    return render(request, 'channels/detail_channel.html', context)


@login_required(login_url='/auth/login/')
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
