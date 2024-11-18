from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .models import Employee
from .serializers import EmployeeSerializer, EmploymentStatusSerializer
import random

# Create your views here.
@api_view(['GET'])
def getActiveEmployees(request, format=None):
    active_Employees = Employee.objects.filter(employmentstatus='active')
    serializer = EmployeeSerializer(active_Employees, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def getActiveManagerID(request, format=None):
    active_ManagerID = Employee.objects.filter(employmentstatus='active', type='Manager').values_list('employeeid', flat=True)
    return Response(active_ManagerID)


@api_view(['GET'])
def getEmployeeInfo(request, employeeid, format=None):
    try:
        employee = Employee.objects.get(pk=employeeid)
    except Employee.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    serializer = EmployeeSerializer(employee)
    return Response(serializer.data)

@api_view(['Get'])
def getValidEmployeeID(request, format=None):
    existing_ids = set(Employee.objects.values_list('employeeid', flat=True))
    lowest_id = 10000
    highest_id = 99999
    
    new_id = random.randint(lowest_id, highest_id)
    while new_id in existing_ids:
        new_id = random.randint(lowest_id, highest_id)

    return Response({"employeeid": new_id})


@api_view(['POST'])
def addEmployee(request, format=None):
    name = request.data.get('name')
    emp_type = request.data.get('type')

    # input validation
    if not name or not emp_type:
        return Response({"error": "Name and type fields required."}, status=status.HTTP_400_BAD_REQUEST)

    # generate new id
    existing_ids = set(Employee.objects.values_list('employeeid', flat=True))
    lowest_id = 10000
    highest_id = 99999

    new_id = random.randint(lowest_id, highest_id)
    while new_id in existing_ids: 
        new_id = random.randint(lowest_id, highest_id) # make unique

    # create instance
    employee_data = {
        "employeeid": new_id,
        "name": name,
        "type": emp_type,
        "employmentstatus": "active"
    }

    serializer = EmployeeSerializer(data=employee_data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # bad request if input is incorrect

@api_view(['PATCH'])
def fireEmployee(request, employeeid, format=None):
    #verify id exists
    try:
        employee = Employee.objects.get(pk=employeeid)
    except Employee.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    employee.employmentstatus = 'inactive'
    employee.save()

    serializer = EmploymentStatusSerializer(employee)
    return Response(serializer.data, status=status.HTTP_200_OK)