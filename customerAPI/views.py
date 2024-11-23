from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import CustomerInfo
from django.contrib.auth.hashers import make_password, check_password #hashing for passwords 

@api_view(['POST'])
def add_customer(request):
    username = request.data.get('username')
    password = request.data.get('password')

    #input validation; included both fields, conforms to length reqs, username DNE
    if not username or not password:
        return Response({"error": "'username' and 'password' required."}, status=status.HTTP_400_BAD_REQUEST)
    
    if len(username) > 150:
        return Response({"error": "Username capped at 150 characters"}, status=status.HTTP_400_BAD_REQUEST)

    if len(password) > 128:
        return Response({"error": "Password capped at 128 characters"}, status=status.HTTP_400_BAD_REQUEST)

    if CustomerInfo.objects.filter(username=username).exists():
        return Response({"error": "Username is taken."}, status=status.HTTP_400_BAD_REQUEST)

    hashed_password = make_password(password) #hash password so nobody takes our chicken money
    

    new_customer = CustomerInfo.objects.create(
        username=username,
        password=hashed_password
    )

    # 
    return Response({
        "message": "Customer created.",
        "username": new_customer.username,
        "discounts_available": new_customer.discounts_available,
        "total_spent": new_customer.total_spent,
        "total_savings": new_customer.total_savings
    }, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def login_customer(request):
    username = request.data.get('username')
    password = request.data.get('password')

    # input validation
    if not username or not password:
        return Response({"error": "'username' and 'password' required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        customer = CustomerInfo.objects.get(username=username)
    except CustomerInfo.DoesNotExist:
        return Response({"error": "Invalid username."}, status=status.HTTP_404_NOT_FOUND)

    #check password
    if check_password(password, customer.password):
        return Response({
            "message": "Login successful.",
            "username": customer.username,
            "discounts_available": customer.discounts_available,
            "total_savings": round(customer.total_savings, 2)
        }, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Invalid password for given username."}, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['POST'])
def apply_discounts(request):
    username = request.data.get('username')
    discounts_applied = request.data.get('discounts_applied')
    total_before_discount = request.data.get('total_before_discount') 
    #just added to avoid any differences in the calc between front and back. Also will allow us to change % per discount much easier if we want
    total_after_discount = request.data.get('total_after_discount')

    #input validation
    if not username or discounts_applied is None or total_before_discount is None or total_after_discount is None:
        return Response({
            "error": "'username', 'discounts_applied', 'total_before_discount' and 'total_after_discount' are required."}, 
            status=status.HTTP_400_BAD_REQUEST)

    if (not isinstance(discounts_applied, int) 
        or not isinstance(total_before_discount, (int, float)) 
        or not isinstance(total_after_discount, (int, float))):
        return Response({
            "error": "'discounts_applied' must be int and 'total_before_discount' and 'total_after_discount' must be a number"}, 
            status=status.HTTP_400_BAD_REQUEST)
    if total_before_discount < total_after_discount:
        return Response({
            "error": "'total_before_discount' must be greater than or equal to 'total_after_discount'."}, 
            status=status.HTTP_400_BAD_REQUEST)


    #check username
    try:
        customer = CustomerInfo.objects.get(username=username)
    except CustomerInfo.DoesNotExist:
        return Response({"error": "Customer not found."}, status=status.HTTP_404_NOT_FOUND)

    # validation for discounts applied
    if discounts_applied > customer.discounts_available:
        return Response({"error": "Not enough discounts available."}, status=status.HTTP_400_BAD_REQUEST)

    #make changes to fields
    if discounts_applied > 0:
        customer.discounts_available -= discounts_applied
    
    #recalculate discounts_available
    previous_spent = customer.total_spent
    customer.total_spent += total_after_discount

    old_progress = previous_spent % 20
    current_progress = total_after_discount + old_progress  
    new_discounts = current_progress // 20
    customer.discounts_available += new_discounts

    #calculate total savings 
    if discounts_applied > 0:
        savings = total_before_discount - total_after_discount
        customer.total_savings += savings

    customer.save()

    #return updated fields for customer (not total spent, seeing how much you have spent somewhere might discourage future spending)
    return Response({
        "message": "Discounts applied successfully.",
        "username": customer.username,
        "discounts_available": int(customer.discounts_available),
        "total_savings": round(customer.total_savings, 2)
    }, status=status.HTTP_200_OK)
