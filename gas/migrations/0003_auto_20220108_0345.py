# Generated by Django 3.2.7 on 2022-01-08 02:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gas', '0002_auto_20220108_0331'),
    ]

    operations = [
        migrations.AlterField(
            model_name='station',
            name='address',
            field=models.CharField(max_length=128, verbose_name='Dirección'),
        ),
        migrations.AlterField(
            model_name='station',
            name='locality',
            field=models.CharField(max_length=64, verbose_name='Localidad'),
        ),
        migrations.AlterField(
            model_name='station',
            name='postal_code',
            field=models.CharField(max_length=5, verbose_name='Código postal'),
        ),
        migrations.AlterField(
            model_name='station',
            name='province',
            field=models.CharField(max_length=64, verbose_name='Provincia'),
        ),
        migrations.AlterField(
            model_name='station',
            name='schedule',
            field=models.CharField(max_length=64, verbose_name='Horario'),
        ),
    ]
