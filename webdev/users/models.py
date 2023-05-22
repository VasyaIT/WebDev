from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

User = get_user_model()


class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='account')
    is_premium = models.BooleanField('Premium account', default=False)
    rating = models.FloatField('User rating', help_text='Range from 1 to 5', default=None,
                               blank=True, null=True,
                               validators=[MinValueValidator(1), MaxValueValidator(5)])
    about = models.CharField('User description', max_length=80, blank=True)
    avatar = models.ImageField('User avatar', blank=True)

    def __str__(self):
        return self.user.username


class Subscribe(models.Model):
    user_from = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rel_from_set')
    user_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rel_to_set')
    created_at = models.DateTimeField(auto_now_add=True)


User.add_to_class('subscribing',
                  models.ManyToManyField(
                      'self', through=Subscribe,
                      related_name='subscribers',
                      symmetrical=False))
