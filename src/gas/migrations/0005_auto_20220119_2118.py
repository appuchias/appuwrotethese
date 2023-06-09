# Generated by Django 3.2.7 on 2022-01-19 20:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gas', '0004_auto_20220110_0010'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='locality',
            options={'verbose_name': 'Locality', 'verbose_name_plural': 'Localities'},
        ),
        migrations.AlterModelOptions(
            name='postalcode',
            options={'verbose_name': 'Postal code', 'verbose_name_plural': 'Postal codes'},
        ),
        migrations.AlterModelOptions(
            name='province',
            options={'verbose_name': 'Province', 'verbose_name_plural': 'Provinces'},
        ),
        migrations.AlterModelOptions(
            name='station',
            options={'ordering': ['id_eess'], 'verbose_name': 'Gas station', 'verbose_name_plural': 'Gas stations'},
        ),
        migrations.AlterField(
            model_name='locality',
            name='name',
            field=models.CharField(max_length=64, verbose_name='Locality'),
        ),
        migrations.AlterField(
            model_name='postalcode',
            name='postal_code',
            field=models.IntegerField(verbose_name='Postal code'),
        ),
        migrations.AlterField(
            model_name='province',
            name='name',
            field=models.CharField(max_length=64, verbose_name='Province'),
        ),
        migrations.AlterField(
            model_name='station',
            name='address',
            field=models.CharField(max_length=128, verbose_name='Address'),
        ),
        migrations.AlterField(
            model_name='station',
            name='company',
            field=models.CharField(max_length=128, verbose_name='Company'),
        ),
        migrations.AlterField(
            model_name='station',
            name='last_update',
            field=models.DateTimeField(auto_now=True, verbose_name='Last update'),
        ),
        migrations.AlterField(
            model_name='station',
            name='latitude',
            field=models.CharField(default='0', max_length=10, verbose_name='Latitude'),
        ),
        migrations.AlterField(
            model_name='station',
            name='longitude',
            field=models.CharField(default='0', max_length=10, verbose_name='Longitude'),
        ),
        migrations.AlterField(
            model_name='station',
            name='price_history',
            field=models.JSONField(default=dict, verbose_name='History'),
        ),
        migrations.AlterField(
            model_name='station',
            name='prices',
            field=models.JSONField(default=dict, verbose_name='Prices'),
        ),
        migrations.AlterField(
            model_name='station',
            name='schedule',
            field=models.CharField(max_length=64, verbose_name='Schedule'),
        ),
    ]
