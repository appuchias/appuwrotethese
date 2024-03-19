# Generated by Django 4.2.7 on 2024-03-19 23:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("gas", "0023_stationprice_price_gob_alter_station_locality_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="station",
            name="locality",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="gas.locality"
            ),
        ),
        migrations.AlterField(
            model_name="station",
            name="province",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="gas.province"
            ),
        ),
    ]
