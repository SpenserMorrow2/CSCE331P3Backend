from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.db.models import Max
from .models import MenuItem, ItemPrice, MenuCalories
from inventoryAPI.models import RawInventory, MenuRawJunction
from .serializers import MenuSerializer, PriceSerializer
from django.http import HttpResponse
from django.http import FileResponse
from P3BackEnd import settings
import os
import requests


##Simple Get Functions returning Lists
@api_view(['GET'])
def MenuItems(request, format=None):
    if request.method == 'GET': 
        menu_items = MenuItem.objects.all()
        serializer = MenuSerializer(menu_items, many=True)
        return Response(serializer.data)

@api_view(['GET'])
def MenuItemNames(request, format=None):
    names = MenuItem.objects.values_list('name', flat=True)
    return Response(names)

## get, given 
@api_view(['GET'])
def MenuItemDetail(request, id, format=None):
    try:
        menuItem = MenuItem.objects.get(pk=id)
    except MenuItem.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    serializer = MenuSerializer(menuItem)
    return Response(serializer.data)

@api_view(['GET'])
def MenuItemPrice(request, id, format=None):
    try:
        prices = ItemPrice.objects.get(pk=id)
    except MenuItem.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    serializer = PriceSerializer(prices)
    return Response(serializer.data)

#helper for add menu; checks existing inventory id's passed
def validate_addMenu_rawItems(name, type, associated_inventory):
    errors = {}

    # name validation
    if not name or not isinstance(name, str):
        errors['name'] = 'Name field is required as string'

    # type validation
    if not type or not isinstance(type, str):
        errors['type'] = 'Type field is required as string'

    # rawitems validation
    if not isinstance(associated_inventory, list):
        errors['rawitems'] = 'Raw Items Required as list'
    else:
        invalid_items = [item for item in associated_inventory if not isinstance(item, int)]
        if invalid_items:
            errors['rawitems'] = 'All rawItems bust be integers'

        # verify existence
        non_existent_items = [item for item in associated_inventory if not RawInventory.objects.filter(rawitemid=item).exists()]
        if non_existent_items:
            errors['rawitems'] = f"The rawID's don't exist: {non_existent_items}"

    return errors

#helper for add menu; checks that all fields are there for creating new inventory item
def validate_addMenu_newRawItems(inventory_items):
    errors = []

    if not isinstance(inventory_items, list):
        return {"new_inventory_items": "Must be a list"}

    for index, item in enumerate(inventory_items):
        item_errors = {}
        
            # name validation
        if 'name' not in item or not isinstance(item['name'], str) or not item['name'].strip():
            item_errors['name'] = 'name field is required as string'

            # quantity validation
        if 'quantity' not in item or not isinstance(item['quantity'], int):
            item_errors['quantity'] = 'quantity field is required as integer.'

            # Validate 'min' - must be provided and be an integer
        if 'min' not in item or not isinstance(item['min'], int):
            item_errors['min'] = 'min field is required integer.'

            # index w/ errors to target request error
        if item_errors:
            errors.append({f"item_{index}": item_errors})

    return errors

#helper for add menu; validates prices for new menu item
def validate_prices(prices):
    if not isinstance(prices, list) or len(prices) != 3:
        return "Price must be list of 3 floats"
    
    if not all(isinstance(price, (int, float)) for price in prices):
        return "Price must be list of 3 floats"
    
    return None  # none if passes

#helper for add menu; makes junction entries 
def create_junction_entries(associated_inventory, itemid):
    
    next_junction_id = 1 + (MenuRawJunction.objects.aggregate(Max('junctionid'))['junctionid__max'] or 0)
    
    # create junction entries for each raw item in associatedInventory
    for raw_item_id in associated_inventory:
        MenuRawJunction.objects.create(
            junctionid=next_junction_id,
            rawitemid=raw_item_id,
            itemid=itemid,
        )
        next_junction_id += 1  # increment for each new junction entry

@api_view(['POST'])
def addMenuItem(request, format=None): 
    newName = request.data.get('name')
    newType = request.data.get('type')
    prices = request.data.get('prices')
    associatedInventory = request.data.get('rawitems', [])
    new_inventory_items = request.data.get('new_inventory_items', [])
    calories = request.data.get('calories')
    serving_size = request.data.get('serving_size')

    
    #input validation w/ helper function
    inventory_errors = validate_addMenu_rawItems(newName, newType, associatedInventory)
    newInventory_errors = validate_addMenu_newRawItems(new_inventory_items)
    prices_error = validate_prices(prices)

    calorie_errors = {}
    if not calories or not isinstance(calories, str) or len(calories) > 10:
        calorie_errors['calories'] = "calories must be a non-empty string with a max length of 10."
    if not serving_size or not isinstance(serving_size, str) or len(serving_size) > 10:
        calorie_errors['serving_size'] = "serving size must be a non-empty string with a max length of 10."

    if inventory_errors or newInventory_errors or prices_error or calorie_errors:
        combined_errors = {**inventory_errors, **calorie_errors}
        if newInventory_errors:
            combined_errors['new_inventory_items'] = newInventory_errors
        if prices_error:
            combined_errors['prices'] = prices_error
        return Response(combined_errors, status=status.HTTP_400_BAD_REQUEST)

    nextID = 1 + (MenuItem.objects.aggregate(Max('itemid'))['itemid__max'])
   

    newMenuItem = MenuItem.objects.create( 
        itemid = nextID,
        name = newName,
        type = newType,
    ) 
        # create saves new entry in database
        
    ItemPrice.objects.create(
        itemid=nextID,
        smallprice=prices[0],
        medprice=prices[1],
        largeprice=prices[2]
    )

    MenuCalories.objects.create(
        itemid=nextID,
        calories=calories,
        serving_size=serving_size
    ) #create menu calorie entries

    
        # create junction entries for raw items associated, if provided
    if associatedInventory:
        create_junction_entries(associatedInventory, nextID)

    
        # create new inventory/junction entries if provided
    new_rawID = []
    for item in new_inventory_items:
        nextInventoryID = 1 + (RawInventory.objects.aggregate(Max('rawitemid'))['rawitemid__max'])
        RawInventory.objects.create(
            rawitemid = nextInventoryID,
            name = item['name'],
            quantity = item['quantity'],
            min = item['min']
        )
        new_rawID.append(nextInventoryID)
    if (len(new_rawID) > 0):
        create_junction_entries(new_rawID, nextID)

    return Response(status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
def removeMenuItem(request, removalid, format=None):
        # validate id
    if not removalid or not isinstance(removalid, int): #check int
        return Response({"error": "itemid is required and must be an integer."}, status=status.HTTP_400_BAD_REQUEST)
    
        #ensure not key item (key items are those essential to the standard panda menu)
    if (removalid <= 26):
        return Response({"error: Can't delete a key item"})

        # verify exists
    try:
        menu_item = MenuItem.objects.get(itemid=removalid)
    except MenuItem.DoesNotExist:
        return Response({"error": "Given menu id doesn't exist"}, status=status.HTTP_404_NOT_FOUND)

    
        # delete all junction entries associated with the itemid
    MenuRawJunction.objects.filter(itemid=removalid).delete()

    try:
        item_price = ItemPrice.objects.get(itemid=removalid)
        item_price.delete()
    except ItemPrice.DoesNotExist:
        pass
    
    #delete associated calorie entry too
    try:
        calorie_entry = MenuCalories.objects.get(itemid=removalid)
        calorie_entry.delete()
    except MenuCalories.DoesNotExist:
        pass

        # delete MenuItem entry
    menu_item.delete()

    return Response({"message": f"MenuItem with itemid {removalid} and its associated junction entries have been deleted."}, status=status.HTTP_200_OK)

@api_view(['PATCH'])
def changeSmallPrice(request, itemid):
    new_price = request.data.get('new_price')
    return change_price(itemid, new_price, 'smallprice')

@api_view(['PATCH'])
def changeMediumPrice(request, itemid):
    new_price = request.data.get('new_price')
    return change_price(itemid, new_price, 'medprice')

@api_view(['PATCH'])
def changeLargePrice(request, itemid):
    new_price = request.data.get('new_price')
    return change_price(itemid, new_price, 'largeprice')

def change_price(itemid, new_price, field_name):
    #validate id and new price
    if not isinstance(itemid, int):
        return Response({"error": "Item ID must be an integer."}, status=status.HTTP_400_BAD_REQUEST)
    
    if new_price is None or not isinstance(new_price, (int, float)):
        return Response({"error": "New price must be a number."}, status=status.HTTP_400_BAD_REQUEST)

    #find the associated entry
    try:
        item_price = ItemPrice.objects.get(itemid=itemid)
    except ItemPrice.DoesNotExist:
        return Response({"error": "Price entry not found matching id"}, status=status.HTTP_404_NOT_FOUND)

    #update field
    setattr(item_price, field_name, new_price)
    item_price.save()

    return Response({
        "message": f"{field_name.capitalize()} successfully updated.",
        "itemid": itemid,
        "new_price": new_price
    }, status=status.HTTP_200_OK)



@api_view(['GET'])
def MenuItemPicture(request, itemID, format=None):
    # Define the path to the image file (make sure the file exists)
    image_filename = str(itemID) + ".png"
    image_path = "/MenuItemPictures/" + image_filename #os.path.join(settings.MEDIA_ROOT, image_filename)
        #print(image_path)
        # Check if the image exists
        #if os.path.exists(image_path):
            # Return the image with the correct content type
    return Response({"image_url": image_path})
    

@api_view(['POST'])
def UploadItemPicture(request, itemID, format=None):
    #image_url = request.data.get('image_url')
    image = request.FILES['image']
    image_dir=settings.MEDIA_ROOT 
    #image.name=str(itemID)+".png"
    file_path = os.path.join(image_dir, image.name)
    with open(file_path, 'wb+') as destination:
        for chunk in image.chunks():
            destination.write(chunk)
    return Response({'message': 'Image uploaded successfully!', 'file_path': file_path}, status=200)
    

@api_view(['DELETE'])
def DeleteItemImage(request, itemID, format=None):
    
    image_name = str(itemID)+ ".png"

    file_path = os.path.join(settings.MEDIA_ROOT, image_name)

    if os.path.exists(file_path):
        os.remove(file_path)
        return Response({"success": "Image deleted successfully."})
    else:
        return Response({"error": "Image file not found."}, status=404)
