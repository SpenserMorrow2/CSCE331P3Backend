from django.db import models

class OrderInfo(models.Model):
    orderid = models.IntegerField(primary_key=True)
    totalprice = models.FloatField(blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    time = models.TimeField(blank=True, null=True)

    class Meta:
        db_table = 'order_info'

class OrderItems(models.Model):
    orderid = models.IntegerField(blank=True, null=True)
    itemid = models.IntegerField(blank=True, null=True)
    size = models.TextField(blank=True, null=True)
    entryid=models.AutoField(primary_key=True)

    class Meta:
        db_table = 'order_items'

class ActiveKitchenOrders(models.Model):
    entryid = models.IntegerField(blank=True, null=True)
    orderid= models.IntegerField(blank=True, null=True)
    
    class Meta:
        db_table = 'active_kitchen_orders'