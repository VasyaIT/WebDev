# Generated by Django 4.2 on 2023-05-29 11:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_alter_account_avatar'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='avatar',
            field=models.ImageField(blank=True, upload_to='', verbose_name='User avatar'),
        ),
    ]
