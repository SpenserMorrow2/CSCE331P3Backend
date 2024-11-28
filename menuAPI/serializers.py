from rest_framework import serializers
from .models import MenuItem, ItemPrice, MenuCalories
from P3BackEnd import settings
import os

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
    calorie_info = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()


    class Meta:
        model = MenuItem
        fields = ['itemid', 'name', 'type', 'price_info', 'calorie_info', 'image_url']

    def get_price_info(self, obj):
        #use NestedPriceSerializer to exclude itemid
        price = ItemPrice.objects.get(itemid=obj.itemid)
        return NestedPriceSerializer(price).data
    
    def get_calorie_info(self, obj):
        try:
            calorie_entry = MenuCalories.objects.get(itemid=obj.itemid)
            return {
                'calories': calorie_entry.calories,
                'serving_size': calorie_entry.serving_size
            }
        except MenuCalories.DoesNotExist:
            return None
    
    def get_image_url(self, obj):
        # Define the path to the image file (make sure the file exists)
        image_filename = str(obj.itemid) + ".jpg"
        image_path = os.path.join(settings.MEDIA_ROOT, image_filename)
        #print(image_path)
        # Check if the image exists
        if os.path.exists(image_path):
            # Return the image with the correct content type
            return image_path
        else:
            # Handle case where image doesn't exist
            return None
    
