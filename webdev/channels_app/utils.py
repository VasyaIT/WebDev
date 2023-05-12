from random import choice, randint
import string
from time import time

from django.utils.text import slugify


def save_channel_form(form, request) -> None:
    """Saving form if it is valid"""
    channel = form.save(commit=False)
    channel.author = request.user
    generate_slug(channel)
    channel.save()
    form.save_m2m()


def generate_slug(channel):
    """Generating channel slug"""
    random_number = randint(5, 15)
    slug_string = string.ascii_lowercase
    rand_string = ''.join(choice(slug_string) for i in range(random_number))
    channel.slug = f'{slugify(channel.name)}-{str(int(time()))}_{rand_string}'
