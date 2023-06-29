from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import Count
from django.urls import reverse

from channels_app.utils import generate_slug


User = get_user_model()


class OnlineManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().annotate(online=Count('current_users')).order_by('-online')


class Tag(models.Model):
    name = models.CharField('search tags', max_length=30, help_text='Enter the search tags')
    slug = models.SlugField('URL', max_length=255, unique=True, db_index=True, help_text='URL')

    class Meta:
        ordering = ['-id']
        indexes = [models.Index(fields=['id', 'slug'])]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('detail_tag', args=[self.slug])


class Channel(models.Model):
    name = models.CharField('name', max_length=50, help_text='Enter the channel name')
    slug = models.SlugField('URL', max_length=255, unique=True, db_index=True, help_text='URL',
                            null=False, blank=False)
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
    author = models.OneToOneField(
        User, verbose_name='channel author',
        on_delete=models.CASCADE,
        related_name='channels'
    )
    date = models.DateTimeField('channel creation date', auto_now_add=True)
    current_users = models.ManyToManyField(
        User,
        related_name="current_channels",
        help_text='Select the current channel users',
        blank=True
    )

    objects = models.Manager()
    online = OnlineManager()

    class Meta:
        ordering = ['-id']
        indexes = [models.Index(fields=['-date'])]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('detail_channel', args=[self.slug])

    def save(self, *args, **kwargs):
        self.slug = generate_slug(self.name)
        return super().save()


class Message(models.Model):
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name="messages")
    text = models.TextField(max_length=500, null=False, blank=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-id']
        indexes = [models.Index(fields=['-created_at'])]

    def __str__(self):
        return self.text
