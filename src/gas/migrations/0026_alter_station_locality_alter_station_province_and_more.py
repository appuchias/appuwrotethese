# Generated by Django 5.0.4 on 2024-04-17 12:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("gas", "0025_stationprice_price_g95e10_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="station",
            name="locality",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.DO_NOTHING, to="gas.locality"
            ),
        ),
        migrations.AlterField(
            model_name="station",
            name="province",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.DO_NOTHING, to="gas.province"
            ),
        ),
        migrations.AlterField(
            model_name="stationprice",
            name="station",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.DO_NOTHING, to="gas.station"
            ),
        ),
    ]
