# Generated by Django 4.2.1 on 2023-06-02 14:43

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("gas", "0020_remove_station_last_update"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="stationprice",
            options={
                "get_latest_by": ["date", "station"],
                "ordering": ["-date", "station"],
                "verbose_name": "Gas station price",
                "verbose_name_plural": "Gas station prices",
            },
        ),
        migrations.RenameField(
            model_name="stationprice",
            old_name="price_g95",
            new_name="price_g95e5",
        ),
        migrations.RenameField(
            model_name="stationprice",
            old_name="price_g98",
            new_name="price_g98e5",
        ),
    ]
