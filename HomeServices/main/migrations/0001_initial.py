# Generated by Django 5.0.7 on 2024-07-24 17:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='House',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(max_length=255, verbose_name='Адресс дома')),
            ],
        ),
        migrations.CreateModel(
            name='Tariff',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('service', models.CharField(max_length=255)),
                ('price_per_unit', models.FloatField(verbose_name='Цена за <django.db.models.fields.CharField>')),
            ],
        ),
        migrations.CreateModel(
            name='Apartment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=255, verbose_name='Номер квартиры')),
                ('area', models.FloatField(verbose_name='Площадь квартиры')),
                ('house', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='apartments', to='main.house')),
            ],
        ),
        migrations.CreateModel(
            name='WaterMeter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('readings', models.JSONField(verbose_name='Показания счетчика')),
                ('apartment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='water_meters', to='main.apartment')),
            ],
        ),
    ]
