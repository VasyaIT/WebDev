from django.contrib import admin

from .models import Account, Subscribe


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
