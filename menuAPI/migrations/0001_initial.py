# Generated by Django 4.2.16 on 2024-10-28 21:27

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ItemPrice',
            fields=[
                ('itemid', models.IntegerField(primary_key=True, serialize=False)),
                ('smallprice', models.FloatField(blank=True, null=True)),
                ('medprice', models.FloatField(blank=True, null=True)),
                ('largeprice', models.FloatField(blank=True, null=True)),
            ],
            options={
                'db_table': 'item_price',
            },
        ),
        migrations.CreateModel(
            name='MenuItem',
            fields=[
                ('itemid', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.TextField(blank=True, null=True)),
                ('type', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'menu_item',
            },
        ),
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
                ('entryID', models.AutoField(primary_key=True, serialize=False)),
            ],
            options={
                'db_table': 'order_items',
            },
        ),
    ]
