from django.contrib import admin
from .models import Channel, Tag


@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'author', 'date', 'tag', 'slug',)
    list_display_links = ('name',)
    search_fields = ('name', 'tag')
    list_editable = ('tag',)
    empty_value_display = '---'
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',)
    list_display_links = ('name',)
    search_fields = ('name',)
    empty_value_display = '---'
