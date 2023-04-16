# Generated by Django 4.2 on 2023-04-16 12:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Enter the search tags', max_length=15, verbose_name='search tags')),
            ],
        ),
        migrations.CreateModel(
            name='Channel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Enter the channel name', max_length=50, verbose_name='name')),
                ('slug', models.SlugField(help_text='URL', max_length=100, unique=True, verbose_name='URL')),
                ('description', models.CharField(help_text='Enter the channel Description', max_length=255, verbose_name='description')),
                ('date', models.DateTimeField(auto_now_add=True, verbose_name='channel creation date')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='channels', to=settings.AUTH_USER_MODEL, verbose_name='channel author')),
                ('tag', models.ForeignKey(default='Tags are missing', help_text='Choose the search tags', on_delete=django.db.models.deletion.SET_DEFAULT, related_name='channels', to='channels_app.tag', verbose_name='channel tags')),
            ],
        ),
    ]
