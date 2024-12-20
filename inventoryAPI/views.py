from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .models import MenuRawJunction, RawInventory
from menuAPI.models import MenuItem
from .serializers import InventorySerializer
from django.db.models import Max

# Create your views here.
@api_view(['GET'])
def getInventoryItems(request, format=None):
    inventory_items = RawInventory.objects.all()
    serializer = InventorySerializer(inventory_items, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def getInventoryNames(request, format=None):
    rawNames = RawInventory.objects.values_list('name', flat=True)
    return Response(rawNames)

@api_view(['GET'])
def getInventoryDetails(request, rawitemid, format=None):
    rawid = rawitemid
    try:
        inventory_item = RawInventory.objects.get(pk=rawid)
    except RawInventory.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    serializer = InventorySerializer(inventory_item)
    return Response(serializer.data)

@api_view(['GET'])
def getNextRawID(request, format=None):
    max_itemid = RawInventory.objects.aggregate(Max('rawitemid'))['rawitemid__max']
    nextID = max_itemid + 1
    return Response({'value': nextID})

@api_view(['GET'])
def getNextJunctionID(request, format=None):
    max_junctionid = MenuRawJunction.objects.aggregate(Max('junctionid'))['junctionid__max']
    nextID = max_junctionid + 1
    return Response({'value': nextID})

@api_view(['Get'])
def getRawInventoryForMenuItem(request, itemid, format=None):
    inventory_ids = MenuRawJunction.objects.filter(itemid=itemid).values_list('rawitemid', flat=True) #get ids
    raw_inventory_items = RawInventory.objects.filter(rawitemid__in=inventory_ids).values('rawitemid', 'name') #get names 
    return Response(list(raw_inventory_items), status=200)

#helper for add inventory; makes junction entries to given menu item id
def create_junction_entries(associated_menuItems, inventoryid):
    
    next_junction_id = 1 + (MenuRawJunction.objects.aggregate(Max('junctionid'))['junctionid__max'] or 0)
    
    # create junction entries for each raw item in associatedInventory
    for item_id in associated_menuItems:
        MenuRawJunction.objects.create(
            junctionid=next_junction_id,
            rawitemid=inventoryid,
            itemid=item_id,
        )
        next_junction_id += 1  # increment for each new junction entry

#helper for add inventory; validates all fields for invemtory and menu items list
def validate_add_inventory_input(name, quantity, min_value, associated_menu_items):
    errors = {}

    # name validation
    if not isinstance(name, str) or not name.strip():
        errors['name'] = 'name required as string'

    # quantity validation
    if not isinstance(quantity, int):
        errors['quantity'] = 'quantity required as int'

    # min validation
    if not isinstance(min_value, int):
        errors['min'] = 'min required as int'

    # menu validation
    if not isinstance(associated_menu_items, list):
        errors['associatedMenuItems'] = 'associatedMenuItems requires as list of menu item id'
    else:
        invalid_items = [item for item in associated_menu_items if not isinstance(item, int)]
        if invalid_items:
            errors['associatedMenuItems'] = 'associatedMenuItems requires as list of menu item id'

        # Check if each menu item ID exists
        non_existent_items = [
            item for item in associated_menu_items if not MenuItem.objects.filter(itemid=item).exists()
        ]
        if non_existent_items:
            errors['associatedMenuItems'] = f"itemid's don't exist: {non_existent_items}"

    return errors


@api_view(['POST'])
def addInventoryItem(request, format=None): 
    newName = request.data.get('name')
    new_quantity = request.data.get('quantity')
    new_min = request.data.get('min')
    associatedMenuItems = request.data.get('menuitems', [])
    

    
    #input validation w/ helper function
    validation_errors = validate_add_inventory_input(newName, new_quantity, new_min, associatedMenuItems)
    if validation_errors:
        return Response(validation_errors, status=status.HTTP_400_BAD_REQUEST)

    nextID = 1 + (RawInventory.objects.aggregate(Max('rawitemid'))['rawitemid__max'])

   

    newInventoryItem = RawInventory.objects.create( 
        rawitemid = nextID,
        name = newName,
        quantity = new_quantity,
        min = new_min
    ) 
        # create saves new entry in database
    
        # create junction entries for menu items associated, if provided
    if associatedMenuItems:
        create_junction_entries(associatedMenuItems, nextID)

    return Response(status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
def removeInventoryItem(request, removalid, format=None):
        # validate id
    if not removalid or not isinstance(removalid, int): #check int
        return Response({"error": "rawitemid is required and must be an integer."}, status=status.HTTP_400_BAD_REQUEST)

        # verify exists
    try:
        raw_item = RawInventory.objects.get(rawitemid=removalid)
    except RawInventory.DoesNotExist:
        return Response({"error": "Given raw id doesn't exist"}, status=status.HTTP_404_NOT_FOUND)

    
        # delete all junction entries associated with the itemid
    MenuRawJunction.objects.filter(rawitemid=removalid).delete()

        # delete MenuItem entry
    raw_item.delete()

    return Response({"message": f"InventoryItem with itemid {removalid} and its associated junction entries have been deleted."}, status=status.HTTP_200_OK)


@api_view(['PATCH'])
def ChangeInventoryMin(request, rawItemID, new_Min, format=None):
    #verify id exists
    try:
        raw_item = RawInventory.objects.get(rawitemid=rawItemID)
    except RawInventory.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    raw_item.min = new_Min
    raw_item.save()

    return Response({"message":f"Minimum quantity for {raw_item.name} changed successfully"}, status=status.HTTP_200_OK)

@api_view(['PATCH'])
def RestockInventory(request, format=None):
    #verify id exists
    try:
        raw_items = RawInventory.objects.all()
    except RawInventory.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    for item in raw_items:
        item.quantity=int(item.min*(1.5))
        item.save()

    return Response({"message":f"Inventory Restock Completed"}, status=status.HTTP_200_OK)


@api_view(['PATCH'])
def RestockInventoryItem(request, rawItemID, quant, format=None):
    #verify id exists
    try:
        raw_item = RawInventory.objects.get(rawitemid=rawItemID)
    except RawInventory.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    raw_item.quantity=raw_item.quantity+quant
    raw_item.save()

    return Response({"message":f"Restock for {raw_item.name} completed"}, status=status.HTTP_200_OK)

@api_view(['PATCH'])
def changeInventoryName(request, rawitemid):
    new_name = request.data.get('name')
    try:
        raw_item = RawInventory.objects.get(rawitemid=rawitemid)
    except RawInventory.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    raw_item.name = new_name
    raw_item.save()

    return Response({"message":f"Name for {raw_item.name} changed successfully"}, status=status.HTTP_200_OK)

@api_view(['Post'])
def createJunctionEntry(request):
    menuID = request.data.get('menuID')
    rawID = request.data.get('rawID')

    #input validation
    if not (menuID >= 0) or not (rawID >= 0):
        return Response(
            {"error": "Both 'menuID' and 'rawID' are required."},status=status.HTTP_400_BAD_REQUEST)
    try:
        # Ensure the referenced IDs exist in their respective tables
        if not MenuItem.objects.filter(itemid=menuID).exists():
            return Response(
                {"error": f"Menu item with ID {menuID} does not exist."},
                status=status.HTTP_404_NOT_FOUND
            )
        if not RawInventory.objects.filter(rawitemid=rawID).exists():
            return Response(
                {"error": f"Raw inventory item with ID {rawID} does not exist."},
                status=status.HTTP_404_NOT_FOUND
            )
    

        next_junction_id = 1 + (MenuRawJunction.objects.aggregate(Max('junctionid'))['junctionid__max'] or 0)
    
        # create junction entry
        MenuRawJunction.objects.create(
            junctionid = next_junction_id,
            rawitemid = rawID,
            itemid = menuID,
        )

        return Response(
            {
                "message": f"Junction entry for raw item {rawID} and menu item {menuID} created successfully.",
                "data": {
                    "junctionid": next_junction_id,
                    "rawitemid": rawID,
                    "menuitemid": menuID
                }
            },
            status=status.HTTP_201_CREATED
        )
    except Exception as e:
        return Response(
            {"error": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['DELETE'])
def deleteJunctionEntry(request):
    menuID = request.data.get('menuID')
    rawID = request.data.get('rawID')

    #input validation
    if not (menuID >= 0) or not (rawID >= 0):
        return Response(
            {"error": "Both 'menuID' and 'rawID' are required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        junction_entry = MenuRawJunction.objects.filter(itemid=menuID, rawitemid=rawID).first()
        if not junction_entry:
            return Response(
                {"error": f"Junction entry for menu item {menuID} and raw item {rawID} does not exist."},
                status=status.HTTP_404_NOT_FOUND
            )

        #delete the junction entry
        junction_entry.delete()

        return Response(
            {"message": f"Junction entry for menu item {menuID} and raw item {rawID} has been deleted."},
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            {"error": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
