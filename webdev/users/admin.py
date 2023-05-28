from django.contrib import admin

from .models import Account, Subscribe, Friend


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'avatar', 'about', 'rating', 'is_premium')
    list_display_links = ('user',)
    search_fields = ('user',)
    empty_value_display = '---'


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
