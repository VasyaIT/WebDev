# Generated by Django 4.2 on 2023-05-25 08:43

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Subscribe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user_from', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rel_from_set', to=settings.AUTH_USER_MODEL)),
                ('user_to', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rel_to_set', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Friend',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_friend', models.BooleanField(default=False, verbose_name='Is_friend?')),
                ('created_at_request', models.DateTimeField(auto_now_add=True)),
                ('created_at_friendship', models.DateTimeField(blank=True, null=True)),
                ('user_from', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='friending', to=settings.AUTH_USER_MODEL)),
                ('user_to', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='friends', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_premium', models.BooleanField(default=False, verbose_name='Premium account')),
                ('rating', models.FloatField(blank=True, default=None, help_text='Range from 1 to 5', null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)], verbose_name='User rating')),
                ('about', models.CharField(blank=True, max_length=80, verbose_name='User description')),
                ('avatar', models.ImageField(blank=True, upload_to='', verbose_name='User avatar')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='account', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddIndex(
            model_name='subscribe',
            index=models.Index(fields=['-created_at'], name='users_subsc_created_654864_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='subscribe',
            unique_together={('user_from', 'user_to')},
        ),
        migrations.AddIndex(
            model_name='friend',
            index=models.Index(fields=['-created_at_request'], name='users_frien_created_bed219_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='friend',
            unique_together={('user_from', 'user_to')},
        ),
    ]