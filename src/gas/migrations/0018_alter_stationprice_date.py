# Generated by Django 4.2.1 on 2023-05-22 22:58

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("gas", "0017_alter_stationprice_options"),
    ]

    operations = [
        migrations.AlterField(
            model_name="stationprice",
            name="date",
            field=models.DateField(db_index=True),
        ),
    ]