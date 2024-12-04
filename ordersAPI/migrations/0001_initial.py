# Generated by Django 4.2.16 on 2024-11-14 21:21

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='OrderInfo',
            fields=[
                ('orderid', models.IntegerField(primary_key=True, serialize=False)),
                ('totalprice', models.FloatField(blank=True, null=True)),
                ('date', models.DateField(blank=True, null=True)),
                ('time', models.TimeField(blank=True, null=True)),
            ],
            options={
                'db_table': 'order_info',
            },
        ),
        migrations.CreateModel(
            name='OrderItems',
            fields=[
                ('orderid', models.IntegerField(blank=True, null=True)),
                ('itemid', models.IntegerField(blank=True, null=True)),
                ('size', models.TextField(blank=True, null=True)),
                ('entryid', models.AutoField(primary_key=True, serialize=False)),
            ],
            options={
                'db_table': 'order_items',
            },
        ),
    ]