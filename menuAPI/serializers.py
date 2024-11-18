from rest_framework import serializers
from .models import MenuItem, ItemPrice

##ItemPrice, MenuRawJunction, OrderInfo, OrderItems not added yet

class PriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemPrice
        fields = ['itemid', 'smallprice', 'medprice', 'largeprice']

#used for returning item info w/ prices. This version excludes id since menu info has it 
class NestedPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemPrice
        fields = ['smallprice', 'medprice', 'largeprice']  

class MenuSerializer(serializers.ModelSerializer):
    price_info = serializers.SerializerMethodField()

    class Meta:
        model = MenuItem
        fields = ['itemid', 'name', 'type', 'price_info']

    def get_price_info(self, obj):
        #use NestedPriceSerializer to exclude itemid
        price = ItemPrice.objects.get(itemid=obj.itemid)
        return NestedPriceSerializer(price).data
