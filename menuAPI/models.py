# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models

class ItemPrice(models.Model):
    itemid = models.IntegerField(primary_key=True)
    smallprice = models.FloatField(blank=True, null=True)
    medprice = models.FloatField(blank=True, null=True)
    largeprice = models.FloatField(blank=True, null=True)

    class Meta:
        db_table = 'item_price'


class MenuItem(models.Model):
    itemid = models.IntegerField(primary_key=True)
    name = models.TextField(blank=True, null=True)
    type = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'menu_item'




