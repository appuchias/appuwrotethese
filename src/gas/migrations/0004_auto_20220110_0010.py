# Generated by Django 3.2.7 on 2022-01-09 23:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("gas", "0003_auto_20220108_0345"),
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
            name="postal_code",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="gas.postalcode"
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
