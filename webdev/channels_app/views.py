from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .forms import ChannelForm
from .models import Channel
from django.template.defaultfilters import slugify

from .utils import pre_channel_save


def index(request):
    channels = Channel.objects.select_related('author', 'tag')
    context = {
        'channels': channels,
    }
    return render(request, 'channels/index.html', context)


@login_required(login_url='/auth/login/')
def detail_channel(request, slug):
    channels = Channel.objects.select_related('tag', 'author').get(slug=slug)
    context = {
        'channels': channels,
        'joined_user': request.user
    }
    return render(request, 'channels/detail_channel.html', context)


@login_required(login_url='/auth/login/')
def create_channel(request):
    error = ''
    form = ChannelForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            channel = form.save(commit=False)
            channel.author = request.user
            channel.slug = slugify(channel.name)
            pre_channel_save(channel)
            return redirect('index')
        else:
            error = 'Incorrect form'

    form = ChannelForm()
    context = {
        'form': form,
        'error': error,
    }

    return render(request, 'channels/create_channel.html', context)
