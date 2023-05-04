# Generated by Django 4.1.1 on 2022-09-30 07:50

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gas", "0010_remove_station_price_history_remove_station_prices_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="station",
            name="postal_code",
            field=models.IntegerField(
                default=0,
                validators=[django.core.validators.MaxValueValidator(99999)],
                verbose_name="Postal code",
            ),
        ),
    ]