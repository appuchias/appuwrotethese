# Generated by Django 3.2.7 on 2022-01-08 02:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Locality',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, verbose_name='Localidad')),
            ],
        ),
        migrations.CreateModel(
            name='PostalCode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('postal_code', models.IntegerField(verbose_name='Código postal')),
            ],
        ),
        migrations.CreateModel(
            name='Province',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, verbose_name='Provincia')),
            ],
        ),
        migrations.CreateModel(
            name='Station',
            fields=[
                ('id_eess', models.IntegerField(primary_key=True, serialize=False, unique=True, verbose_name='ID_EESS')),
                ('company', models.CharField(max_length=128, verbose_name='Compañía')),
                ('address', models.CharField(max_length=256, verbose_name='Dirección')),
                ('schedule', models.CharField(max_length=128, verbose_name='Horario')),
                ('latitude', models.CharField(default='0', max_length=10, verbose_name='Latitud')),
                ('longitude', models.CharField(default='0', max_length=10, verbose_name='Longitud')),
                ('prices', models.JSONField(default=dict, verbose_name='Precios')),
                ('price_history', models.JSONField(default=dict, verbose_name='Historial')),
                ('last_update', models.DateTimeField(auto_now=True, verbose_name='Última actualización')),
                ('locality', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gas.locality')),
                ('postal_code', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gas.postalcode')),
                ('province', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gas.province')),
            ],
            options={
                'verbose_name': 'gasstation',
                'verbose_name_plural': 'gasstations',
                'ordering': ['id_eess'],
            },
        ),
    ]