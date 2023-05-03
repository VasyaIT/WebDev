from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(verbose_name='search tags', max_length=30, help_text='Enter the search tags')
    slug = models.SlugField(verbose_name='URL', max_length=255, unique=True, db_index=True, help_text='URL')

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('detail_tag', args=[self.slug])


class Channel(models.Model):
    name = models.CharField(verbose_name='name', max_length=50, help_text='Enter the channel name')
    slug = models.SlugField(verbose_name='URL', max_length=255, unique=True, db_index=True, help_text='URL', null=False,
                            blank=False)
    description = models.CharField(
        verbose_name='description',
        max_length=255,
        help_text='Enter the channel Description'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='channel tags',
        help_text='Choose the search tags',
        related_name='channels',
    )
    author = models.ForeignKey(User, verbose_name='channel author', on_delete=models.CASCADE, related_name='channels')
    date = models.DateTimeField(auto_now_add=True, verbose_name='channel creation date')
    current_users = models.ManyToManyField(
        User,
        related_name="current_channels",
        help_text='Select the current channel users',
        blank=True
    )

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('detail_channel', args=[self.slug])


class Message(models.Model):
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name="messages")
    text = models.TextField(max_length=500, null=False, blank=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text
