# Generated by Django 4.2.7 on 2024-02-20 18:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mastermind', '0002_game_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='game',
            name='lost',
        ),
        migrations.AddField(
            model_name='game',
            name='finished',
            field=models.BooleanField(default=False),
        ),
    ]
