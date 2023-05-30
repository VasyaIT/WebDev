from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Account, Subscribe, Friend


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'avatar_image', 'about', 'rating', 'is_premium')
    list_display_links = ('user', 'avatar_image')
    search_fields = ('user',)
    empty_value_display = '---'

    def avatar_image(self, obj):
        if obj.avatar:
            return mark_safe('<img src="{}" width="30" height="30">'.format(obj.avatar.url))
        else:
            return mark_safe('<img src="/static/channels_app/img/anonymous.png" width="30" height="30">')

    avatar_image.short_description = 'avatar'


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('user_from', 'user_to', 'created_at')
    list_display_links = ('user_from', 'user_to')
    search_fields = ('user_from', 'user_to')


@admin.register(Friend)
class FriendAdmin(admin.ModelAdmin):
    list_display = ('user_from', 'user_to', 'is_friend', 'created_at_request', 'created_at_friendship')
    list_display_links = ('user_from', 'user_to')
    search_fields = ('user_from', 'user_to')
