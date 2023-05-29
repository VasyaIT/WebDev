from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone

User = get_user_model()


class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='account')
    is_premium = models.BooleanField('Premium account', default=False)
    rating = models.FloatField('User rating', help_text='Range from 1 to 5', default=None,
                               blank=True, null=True,
                               validators=[MinValueValidator(1), MaxValueValidator(5)])
    about = models.TextField('User description', max_length=255, blank=True)
    avatar = models.ImageField('User avatar', blank=True)

    def __str__(self):
        return self.user.username


class Subscribe(models.Model):
    user_from = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rel_from_set')
    user_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rel_to_set')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=['-created_at'])]
        unique_together = ('user_from', 'user_to')

    def __str__(self):
        return f'{self.user_from} subscribed to {self.user_to}'

    def clean(self):
        if self.user_from == self.user_to:
            raise ValidationError('User_from and user_to must be different')


class Friend(models.Model):
    user_from = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friending')
    user_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friends')
    is_friend = models.BooleanField(default=False)
    created_at_request = models.DateTimeField(auto_now_add=True)
    created_at_friendship = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-id']
        indexes = [models.Index(fields=['-created_at_request'])]
        unique_together = ('user_from', 'user_to')

    def __str__(self):
        if self.is_friend:
            return f'{self.user_from} is friends with {self.user_to}'
        return f'{self.user_from} sent a request to {self.user_to}'

    def clean(self):
        tz = timezone.now()

        if self.user_from == self.user_to:
            raise ValidationError('User_from and user_to must be different')

        if self.is_friend:
            self.created_at_friendship = tz
            if not Friend.objects.filter(user_from=self.user_to, user_to=self.user_from).exists():
                Friend.objects.create(user_from=self.user_to, user_to=self.user_from,
                                      is_friend=True, created_at_friendship=tz)

    def save(self, *args, **kwargs):
        qs = Friend.objects.filter(user_from=self.user_to, user_to=self.user_from)
        tz = timezone.now()

        if qs.exists() and not self.is_friend:
            self.is_friend = True
            self.created_at_friendship = tz
            qs.update(is_friend=True, created_at_friendship=tz)

        return super().save()

    def delete(self, *args, **kwargs):
        qs = Friend.objects.filter(user_from=self.user_to, user_to=self.user_from)
        if qs.exists():
            qs.delete()
        return super().delete()


User.add_to_class('subscribing',
                  models.ManyToManyField(
                      'self', through=Subscribe,
                      related_name='subscribers',
                      symmetrical=False))
