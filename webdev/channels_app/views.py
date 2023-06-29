from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import IntegrityError
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from webdev.logger_config import logger
from .decorators import have_channel_required
from .forms import ChannelForm, SearchForm
from .models import Channel, Message, Tag
from .utils import save_channel_form, get_filtered_channels
from .filters import ChannelFilter


User = get_user_model()


def index(request, tag_slug=None):
    """Channel list with search"""
    channels_list = (
        Channel.online.select_related('author')
        .prefetch_related('current_users', 'tags')
    )
    form = SearchForm()
    tags_form = ChannelFilter(request.GET, queryset=channels_list)
    pagination_symbol = '?'
    empty = False
    have_channel = False

    if 'query' in request.GET or 'tags' in request.GET:
        form = SearchForm(request.GET)
        pagination_symbol = f'?{request.GET.urlencode()}&'

        if 'page' in pagination_symbol:
            pagination_symbol = pagination_symbol.split('page')[0]

        if form.is_valid():
            channels_list = get_filtered_channels(
                form.cleaned_data.get('query'), tags_form.qs, channels_list
            )
            if not channels_list:
                empty = True

    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        channels_list = channels_list.filter(tags__in=[tag])

    if request.user.is_authenticated and Channel.objects.filter(author=request.user).exists():
        have_channel = True

    paginator = Paginator(channels_list, 3)
    page_number = request.GET.get('page', 1)

    try:
        channels = paginator.page(page_number)
    except EmptyPage:
        channels = paginator.page(1)
        logger.info(f'{request.user} clicked on the empty paginator page')
    except PageNotAnInteger:
        logger.info(f'{request.user} clicked on the not existing paginator page')
        raise Http404

    context = {
        'channels': channels,
        'tag': tag,
        'form': form,
        'ps': pagination_symbol,
        't_f': tags_form,
        'empty': empty,
        'have_channel': have_channel,
    }
    return render(request, 'channels/index.html', context)


@login_required
def detail_channel(request, slug):
    """Channel with communication. Connect to WebSocket"""
    channels = get_object_or_404(Channel.objects.select_related('author'), slug=slug)
    msgs = (Message.objects.select_related('channel', 'user')
            .filter(channel=channels).order_by('id')[:1000])

    context = {
        'channels': channels,
        'mess': msgs,
    }
    return render(request, 'channels/detail_channel.html', context)


@login_required
def create_update_channel(request):
    """Creating or updating the channel"""
    user = request.user
    channel = Channel.objects.filter(author=user)
    form = ChannelForm()
    button = ''

    if request.path == '/create/':
        button = 'Create'
        if channel.exists():
            messages.warning(request, 'You can only have one created channel')
            return redirect('index')

        form = ChannelForm(request.POST or None)

    elif request.path == '/edit/':
        button = 'Edit'
        if not channel.exists():
            return redirect('create_channel')

        form = ChannelForm(request.POST or None, instance=user.channels)

    if request.method == 'POST':
        if form.is_valid():
            try:
                save_channel_form(form, request)
                if button == 'Create':
                    logger.info(f'{request.user} created the channel')
                    messages.success(request, 'The channel has been successfully created')
                else:
                    logger.info(f'{request.user} updated the channel')
                    messages.success(request, 'The channel has been successfully edited')
                return redirect('detail_channel', user.channels.slug)
            except IntegrityError:
                messages.warning(request, 'Unknown error. Try again')
                logger.warning(f'{request.user} caught an `Unknown error`')
        else:
            messages.warning(request, 'Incorrect form')
            logger.warning(f'{request.user} enter the incorrect form')

    context = {
        'form': form,
        'button': button,
    }

    return render(request, 'channels/create_channel.html', context)


@login_required
@require_POST
@have_channel_required
def delete_channel(request):
    """Deleting the channel"""
    request.user.channels.delete()
    messages.success(request, 'Channel deleted successfully')
    logger.info(f'{request.user} deleted the channel')
    return redirect('index')
