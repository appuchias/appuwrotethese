# Generated by Django 4.2.1 on 2023-05-23 10:58

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("gas", "0018_alter_stationprice_date"),
    ]

    operations = [
        migrations.AlterField(
            model_name="stationprice",
            name="date",
            field=models.DateField(db_index=True, default=django.utils.timezone.now),
        ),
    ]
