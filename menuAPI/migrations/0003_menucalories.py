# Generated by Django 4.2.16 on 2024-11-24 16:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('menuAPI', '0002_delete_orderinfo_delete_orderitems'),
    ]

    operations = [
        migrations.CreateModel(
            name='MenuCalories',
            fields=[
                ('itemid', models.IntegerField(primary_key=True, serialize=False)),
                ('calories', models.CharField(max_length=10)),
                ('serving_size', models.CharField(max_length=10)),
            ],
            options={
                'db_table': 'menu_calories',
            },
        ),
    ]