from django.db import models


class RawInventory(models.Model):
    rawitemid = models.IntegerField(primary_key=True)
    name = models.TextField(blank=True, null=True)
    quantity = models.IntegerField(blank=True, null=True)
    min = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'raw_inventory'

class MenuRawJunction(models.Model):
    junctionid = models.IntegerField(primary_key=True)
    rawitemid = models.IntegerField(blank=True, null=True)
    itemid = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'menu_raw_junction'