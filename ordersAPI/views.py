from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.db.models import Min, Max, Count, Sum
from .models import OrderInfo, OrderItems, ActiveKitchenOrders
from menuAPI.models import MenuItem
from menuAPI.serializers import MenuSerializer
from inventoryAPI.models import RawInventory, MenuRawJunction
from django.utils import timezone
from datetime import datetime


@api_view(['POST'])
def create_order(request):
    total_price = request.data.get('total_price')
    item_ids = request.data.get('item_ids', [])
    sizes = request.data.get('sizes', [])
    
    #input validation
    if total_price is None or not isinstance(total_price, (int, float)): 
        return Response(status=status.HTTP_400_BAD_REQUEST) 
    if not item_ids or not all(isinstance(item_id, int) for item_id in item_ids): 
        return Response(status=status.HTTP_400_BAD_REQUEST)
    if not sizes or not all(isinstance(size, str) for size in sizes):
        return Response(status=status.HTTP_400_BAD_REQUEST)
    if len(item_ids) != len(sizes):
        return Response(status=status.HTTP_400_BAD_REQUEST)

    nextID = 1 + (OrderInfo.objects.aggregate(Max('orderid'))['orderid__max'])
   

    order_info = OrderInfo.objects.create( 
        orderid = nextID,
        totalprice = total_price,
        date = timezone.now().date(),
        time = timezone.now().time()
    ) # create saves new entry in database

    # create associated OrderItems entry for each item
    for item_id, my_size in zip(item_ids, sizes):
        order_item = OrderItems.objects.create(
            orderid = nextID,  
            itemid = item_id,
            size = my_size  
        )

    return Response(status=status.HTTP_201_CREATED)


def AddKitchenOrder(eID, oID):
    newEntryID = eID
    oID = oID
    
    
    errors={}
    
    #input validation w/ helper function
    if not isinstance(newEntryID, int):
        errors['entryid'] = 'quantity required as int'

    # min validation
    if not isinstance(oID, int):
        errors['orderid'] = 'min required as int'

    if errors:
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)


   

    newKitchenOrderItem = ActiveKitchenOrders.objects.create( 
        entryid = newEntryID,
        orderid = oID,
    ) 
    # create saves new entry in database
    

    return Response(status=status.HTTP_201_CREATED)

@api_view(['DELETE'])
def RemoveKitchenOrder(request, format=None):
        # validate id
    entryNum = request.data.get('entryid')
    oID = request.data.get('orderid')

    errors={}
    
    #input validation w/ helper function
    if not entryNum or not isinstance(entryNum, int): #check int
        return Response({"error": "entryid is required and must be an integer."}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        kitchenOrder = ActiveKitchenOrders.objects.get(entryid=entryNum)
    except ActiveKitchenOrders.DoesNotExist:
        return Response({"error": "Given entry id doesn't exist"}, status=status.HTTP_404_NOT_FOUND)

    
        # delete all junction entries associated with the itemid
    MenuRawJunction.objects.filter(rawitemid=oID).delete()

        # delete MenuItem entry
    kitchenOrder.delete()

    return Response({"message": f"ActiveKitchenOrder with entry id {entryNum} has been deleted."}, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_kitchen_orders(request, format=None):
    orderIDs = ActiveKitchenOrders.objects.values_list('orderid', flat=True).order_by('orderid')
    ItemsInOrder=[]
    for id in orderIDs:
        my_list=[]
        itemids=OrderItems.objects.filter(orderid=id).values_list('itemid', flat=True)
        for x in itemids:
            my_list.append(RawInventory.objects.get(rawitemid=x).name)
        ItemsInOrder.append(my_list)

    kitchen_orders=[]
    kitchen_orders.append(orderIDs)
    kitchen_orders.append(ItemsInOrder)
    return Response(kitchen_orders)

def subtract_inventory_stock(raw_item_id, sub_amount):
    """
    Decrements the quantity of an inventory item by the specified amount.
    """
    try:
        raw_item = RawInventory.objects.get(rawitemid=raw_item_id)
        raw_item.quantity -= sub_amount
        raw_item.save()
    except RawInventory.DoesNotExist:
        print(f"Raw item with ID {raw_item_id} not found.")
        
def get_order_id_range(start_date, end_date):
    """
    Given a start and end date, return the range of order IDs during that period.
    """
    try:
        order_range = OrderInfo.objects.filter(date__range=[start_date, end_date]) \
                                       .aggregate(min_orderid=Min('orderid'), max_orderid=Max('orderid'))
        min_order_id = order_range.get('min_orderid')
        max_order_id = order_range.get('max_orderid')
        return [min_order_id, max_order_id] if min_order_id and max_order_id else None
    except OrderInfo.DoesNotExist:
        print("No orders found in the specified date range.")
        return None


def getInventoryName(id):
    rawitemEntry= RawInventory.objects.get(pk=id)
    return Response(rawitemEntry.name)

def count_menu_items_between_order_ids(min_order_id, max_order_id):
    """
    Given a min and max order id, count the number of times each menu item was ordered.
    """
    item_counts = [0] * MenuItem.objects.count()  # Initialize the list of item counts
    
    order_items = OrderItems.objects.filter(orderid__range=[min_order_id, max_order_id]) \
                                    .values('itemid') \
                                    .annotate(item_count=Count('itemid'))
    
    for order_item in order_items:
        item_counts[order_item['itemid']] = order_item['item_count']
        
    return item_counts

def getRawInventory(menuitemID):
    raw_items = MenuRawJunction.objects.filter(itemid=menuitemID).values_list('rawitemid', flat=True)
    
    return raw_items

def calculate_inventory_usage(menu_item_counts):
    """
    Given a list of menu item counts, determine the inventory usage for each inventory item.
    """
    total_inventory_items = RawInventory.objects.count()
    inventory_usage = [0] * total_inventory_items  # Initialize to 0 for all raw items
    
    for menu_item_id, menu_item_count in enumerate(menu_item_counts):
        if menu_item_count > 0:
            raw_items = getRawInventory(menu_item_id)
            for raw_item in raw_items:
                inventory_usage[raw_item] += menu_item_count
                
    return scale_inventory_usage(inventory_usage)

def scale_inventory_usage(inventory_usage):
    """
    Scales the inventory usage based on predefined rules.
    """
    for i, usage in enumerate(inventory_usage):
        if usage == 0:
            continue
        
        if i < 30 or i == 33:  # Raw ingredients and syrups
            adjusted_value = usage // 5 + (1 if usage % 5 != 0 else 0)
            inventory_usage[i] = adjusted_value
        elif i == 32:  # Napkins and forks
            inventory_usage[i] += 5
        elif i == 34:  # Small drinks
            inventory_usage[i] //= 3
        elif i == 35:  # Medium drinks
            inventory_usage[i] //= 3
            if usage % 3 == 1:
                inventory_usage[i] += 1
        elif i == 36:  # Large drinks
            inventory_usage[i] //= 3
            if usage % 3 == 2:
                inventory_usage[i] += 1
                
    return inventory_usage

def make_inventory_changes(inventory_usage_scaled):
    """
    Given a list of scaled inventory usage values, make the necessary changes to the inventory.
    """
    for raw_item_id, usage_amount in enumerate(inventory_usage_scaled):
        if usage_amount > 0:
            subtract_inventory_stock(raw_item_id, usage_amount)

def under_min():
    under_min_items = RawInventory.objects.filter(quantity__lt='min') \
                                           .values('name', 'rawitemid', 'quantity', 'min')

    result = []
    for item in under_min_items:
        result.append(f"{item['name']} ({item['rawitemid']}) has a quantity of {item['quantity']}, which is below the {item['min']} unit minimum value")
        
    return result

last_order_id_checked = 57246 
#will be changed in recent inventory function. allows for changes to only be made on those orders not counted yet
def recent_inventory_usage():
    global last_order_id_checked
    
    most_recent_order_id = OrderInfo.objects.aggregate(Max('orderid'))['orderid__max'] #make changes between last checked and most recent orderid 
    
    if last_order_id_checked == most_recent_order_id:
        print("No new changes")
        return None
    
    menu_item_counts = count_menu_items_between_order_ids(last_order_id_checked, most_recent_order_id)

    last_order_id_checked = most_recent_order_id #update global variable for next call
    
    return calculate_inventory_usage(menu_item_counts)

@api_view(['Get'])
def restockReport(request, format = None):
    recent_inventory = recent_inventory_usage()
    
    if recent_inventory:
        make_inventory_changes(recent_inventory)
    
    return Response(under_min())

def salesReportNames():
    menu_items = MenuItem.objects.exclude(name='N/A')
    return [item.name for item in menu_items]

def salesReportNumbers(start_date, end_date):
    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

    # Get the total count of each item sold within the date range
    sales_counts = OrderItems.objects.filter(date__range=[start_date, end_date]).values('itemid').annotate(count=Count('itemid')).order_by('itemid')

    # Create a list initialized to 0, with one element for each menu item
    item_sales = {item.itemid: 0 for item in MenuItem.objects.all()}
    
    # Populate the sales counts for each menu item
    for sale in sales_counts:
        item_sales[sale['itemid']] = sale['count']
    
    # Return sales numbers in the order of the menu items
    return [item_sales[item.itemid] for item in MenuItem.objects.exclude(name='N/A')]

@api_view(['Get'])
def salesReport(request, start_d, end_d, format = None):
    names=salesReportNames()
    numbers=salesReportNumbers(start_d, end_d)

    sales_report = []
    sales_report.append(names)
    sales_report.append(numbers)

    return Response(sales_report)

@api_view(['Get'])
def product_Usage_Report(request, start_date, end_date, format = None):
    orderIDrange=get_order_id_range(start_date,end_date)

    if not orderIDrange:
        return None
    
    MinOrderRange, MaxOrderRange=orderIDrange

    menuItemCounts=count_menu_items_between_order_ids(MinOrderRange,MaxOrderRange)
    inventoryUsage=calculate_inventory_usage(menuItemCounts)
    
    ProductNames_list=[]
    usage_list=[]

    product_Usage=[]
    # Loop through the inventory usage and get the name for each rawitemid
    for rawitemid, usage_count in enumerate(inventoryUsage):
        if usage_count > 0:  # Only include items that were used
            # Get the name of the inventory item (rawitemid corresponds to the index)
            raw_item_name = getInventoryName(rawitemid)
            ProductNames_list.append(raw_item_name)
            # Add item usage to the product usage list
            usage_list.append(str(usage_count))

    product_Usage.append(ProductNames_list)
    product_Usage.append(usage_list)
    return Response(product_Usage)

@api_view(['Get'])
def X_report(request, format = None):
    # Get the current time and date
    now = datetime.now()
    current_hour = now.hour
    current_minute = now.minute
    current_second = now.second
    current_time = now.strftime('%H:%M:%S')
    start_hour = 10  # start hour is fixed to 10:00 AM
    start_time = "10:00:00"
    today_date = now.date()

    # Prepare the report structure
    hours_list = []
    prices_sums_list = []

    # Create hour range from 10:00 AM to current hour
    for hour in range(start_hour, current_hour + 1):
        hours_list.append(f"{hour}:00:00 - {hour + 1}:00:00")
        prices_sums_list.append("0.00")  # Initialize all sales sums to 0.00

    # The query filters sales between the start time and the current time for today
    orders = OrderInfo.objects.filter(
        date=today_date,
        time__gte=start_time,
        time__lte=current_time
    ).order_by('time')

    # Process the results to sum up prices per hour
    sums = [0.0] * len(hours_list)
    current_hour_index = start_hour
    hour_index = 0  # Index for prices_sums_list

    for order in orders:
        order_hour = order.time.hour
        if order_hour != current_hour_index:
            # When the hour changes, store the current sum and move to the next hour
            sums[hour_index] = round(sums[hour_index], 2)  # Round to 2 decimal places
            hour_index += order_hour-current_hour_index
            current_hour_index = order_hour
        sums[hour_index] += float(order.totalprice)

    # Ensure the last hour's sum is recorded
    sums[hour_index] = round(sums[hour_index], 2)

    # Prepare the final report
    x_report = [hours_list, [str(s) for s in sums]]
    
    return Response(x_report) 

@api_view(['Get'])
def Z_report(request, format = None):
    # Get the current time and date
    now = datetime.now()
    start_hour = 10  # start hour is fixed to 10:00 AM
    start_time = "10:00:00"
    today_date = now.date()
    end_time = "22:00:00"

    # Prepare the report structure
    hours_list = []
    prices_sums_list = []

    # Create hour range from 10:00 AM to current hour
    for hour in range(start_hour, end_time):
        hours_list.append(f"{hour}:00:00 - {hour + 1}:00:00")
        prices_sums_list.append("0.00")  # Initialize all sales sums to 0.00

    # The query filters sales between the start time and the current time for today
    orders = OrderInfo.objects.filter(
        date=today_date,
        time__gte=start_time,
        time__lte=end_time
    ).order_by('time')

    # Process the results to sum up prices per hour
    sums = [0.0] * len(hours_list)
    current_hour_index = start_hour
    hour_index = 0  # Index for prices_sums_list

    for order in orders:
        order_hour = order.time.hour
        if order_hour != current_hour_index:
            # When the hour changes, store the current sum and move to the next hour
            sums[hour_index] = round(sums[hour_index], 2)  # Round to 2 decimal places
            hour_index += order_hour-current_hour_index
            current_hour_index = order_hour
        sums[hour_index] += float(order.totalprice)

    # Ensure the last hour's sum is recorded
    sums[hour_index] = round(sums[hour_index], 2)

    # Prepare the final report
    z_report = [hours_list, [str(s) for s in sums]]
    
    return Response(z_report) 