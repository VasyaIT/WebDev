from django.db import IntegrityError
from django.shortcuts import render, redirect

from .forms import ChannelForm
from .models import Channel
from django.template.defaultfilters import slugify


def index(request):
    channels = Channel.objects.select_related('author', 'tag')
    context = {
        'channels': channels,
    }
    return render(request, 'channels/index.html', context)


def detail_channel(request, slug):
    channels = Channel.objects.select_related('tag', 'author').get(slug=slug)
    context = {
        'channels': channels,
    }
    return render(request, 'channels/detail_channel.html', context)


def create_channel(request):
    error = ''
    slug_error = ''
    form = ChannelForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            channel = form.save(commit=False)
            if not request.user.is_authenticated:
                return redirect('index')
            channel.author = request.user
            channel.slug = slugify(channel.name)
            try:
                channel.save()
            except IntegrityError:
                slug_error = 'At the moment this name is used, try another one'
                context = {
                    'form': form,
                    'error': error,
                    'slug_error': slug_error,
                }
                return render(request, 'channels/create_channel.html', context)
            return redirect('index')
        else:
            error = 'Incorrect form'

    form = ChannelForm()
    context = {
        'form': form,
        'error': error,
        'slug_error': slug_error,
    }

    return render(request, 'channels/create_channel.html', context)
