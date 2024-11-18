from django.contrib import admin
from .models import OrderInfo, OrderItems, ActiveKitchenOrders

admin.site.register(OrderInfo)
admin.site.register(OrderItems)
admin.site.register(ActiveKitchenOrders)