from django.db import models

class CustomerInfo(models.Model):
    username = models.CharField(max_length=150, primary_key=True)  
    password = models.CharField(max_length=128)  # hashed passwords
    total_spent = models.FloatField(default=0.0)  
    discounts_available = models.IntegerField(default=0)  
    total_savings = models.FloatField(default=0.0)  

    class Meta:
        db_table = 'customer_info'
        