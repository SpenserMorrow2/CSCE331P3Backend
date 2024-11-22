from rest_framework import serializers
from .models import OrderInfo, OrderItems

class OrderInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderInfo
        fields = ['orderid', 'totalprice', 'date', 'time']

