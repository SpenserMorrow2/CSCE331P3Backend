from rest_framework import serializers
from .models import Employee

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['employeeid', 'name', 'type', 'employmentstatus']

class EmploymentStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['employmentstatus']