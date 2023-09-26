# Generated by Django 4.2.1 on 2023-05-17 17:24

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("gas", "0014_station_last_update"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="stationprice",
            options={
                "ordering": ["date", "station"],
                "verbose_name": "Gas station price",
                "verbose_name_plural": "Gas station prices",
            },
        ),
        migrations.RemoveConstraint(
            model_name="stationprice",
            name="unique_station_date_combination",
        ),
        migrations.RenameField(
            model_name="stationprice",
            old_name="gasolina_95",
            new_name="price_g95",
        ),
        migrations.RenameField(
            model_name="stationprice",
            old_name="gasolina_98",
            new_name="price_g98",
        ),
        migrations.RenameField(
            model_name="stationprice",
            old_name="glp",
            new_name="price_glp",
        ),
        migrations.RenameField(
            model_name="stationprice",
            old_name="gasoleo_a",
            new_name="price_goa",
        ),
        migrations.RenameField(
            model_name="stationprice",
            old_name="id_eess",
            new_name="station",
        ),
        migrations.AddConstraint(
            model_name="stationprice",
            constraint=models.UniqueConstraint(
                fields=("station", "date"), name="unique_station_date_combination"
            ),
        ),
    ]