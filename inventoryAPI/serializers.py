from rest_framework import serializers
from .models import RawInventory

class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RawInventory
        fields = ['rawitemid', 'name', 'quantity', 'min']