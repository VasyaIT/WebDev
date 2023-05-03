from django.contrib import admin
from .models import Channel, Tag, Message


@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'author', 'slug',)
    list_display_links = ('name',)
    search_fields = ('name', 'tags')
    filter_horizontal = ('current_users', 'tags')
    empty_value_display = '---'
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    list_display_links = ('name',)
    search_fields = ('name',)
    empty_value_display = '---'
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'channel', 'text', 'user', 'created_at')
    list_display_links = ('channel',)
    search_fields = ('name', 'text',)
    empty_value_display = '---'
