from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(verbose_name='search tags', max_length=15, help_text='Enter the search tags')

    def __str__(self):
        return self.name


class Channel(models.Model):
    name = models.CharField(verbose_name='name', max_length=50, help_text='Enter the channel name')
    slug = models.SlugField(verbose_name='URL', max_length=100, unique=True, db_index=True, help_text='URL', null=False)
    description = models.CharField(
        verbose_name='description',
        max_length=255,
        help_text='Enter the channel Description'
    )
    tag = models.ForeignKey(
        Tag,
        verbose_name='channel tags',
        help_text='Choose the search tags',
        related_name='channels',
        on_delete=models.SET_DEFAULT,
        default='Tags are missing'
    )
    author = models.ForeignKey(User, verbose_name='channel author', on_delete=models.CASCADE, related_name='channels')
    date = models.DateTimeField(auto_now_add=True, verbose_name='channel creation date')

    def __str__(self):
        return self.name