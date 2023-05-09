from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, TrigramSimilarity
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import IntegrityError
from django.db.models import Q
from django.http import Http404

from django.shortcuts import render, redirect, get_object_or_404

from .forms import ChannelForm, SearchForm
from .models import Channel, Message, Tag
from .utils import save_channel_form

User = get_user_model()


def index(request, tag_slug=None):
    channels_list = Channel.objects.select_related('author').prefetch_related('current_users', 'tags')
    form = SearchForm()
    pagination_symbol = '?'

    # if 'query' in request.GET:
    #     form = SearchForm(request.GET)
    #     if form.is_valid():
    #         query = form.cleaned_data['query']
    #         search_vector = SearchVector('name', 'description', 'tags__name', 'author')
    #         search_query = SearchQuery(query)
    #         rank = SearchRank(search_vector, search_query)
    #         channels_list = channels_list.annotate(search=search_vector, rank=rank)\
    #             .filter(search=search_query).order_by('-rank')

    # if 'query' in request.GET:
    #     form = SearchForm(request.GET)
    #     if form.is_valid():
    #         query = form.cleaned_data['query']
    #         similarity = TrigramSimilarity('name', query)
    #         print(similarity)
    #         channels_list = channels_list.annotate(similarity=similarity)\
    #             .filter(similarity__gt=0.1).order_by('-similarity')

    if 'query' in request.GET:
        form = SearchForm(request.GET)
        pagination_symbol = f'?query={request.GET["query"]}&'
        if form.is_valid():
            query = form.cleaned_data['query']
            result = (Q
                      (name__icontains=query) | Q(tags__name__icontains=query) | Q
                      (author__username__icontains=query) | Q(description__icontains=query)
                      )
            channels_list = channels_list.filter(result).distinct()

    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        channels_list = channels_list.filter(tags__in=[tag]).select_related('author') \
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
        'form': form,
        'ps': pagination_symbol,
    }
    return render(request, 'channels/index.html', context)


@login_required
def detail_channel(request, slug):
    channels = get_object_or_404(Channel.objects.select_related('author'), slug=slug)
    messages = Message.objects.select_related('channel', 'user').filter(channel=channels).order_by('id')[:50]

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
