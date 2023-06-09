# Generated by Django 4.1.1 on 2022-09-08 07:49

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0005_awtuser_upgrade_uuid"),
    ]

    operations = [
        migrations.AlterField(
            model_name="awtuser",
            name="upgrade_uuid",
            field=models.CharField(
                blank=True,
                max_length=24,
                null=True,
                validators=[
                    django.core.validators.RegexValidator(
                        "^[a-f0-9]{6}-[a-f0-9]{10}-[a-f0-9]{6}$"
                    )
                ],
                verbose_name="Upgrade UUID",
            ),
        ),
    ]
