from django.db import models

class Employee(models.Model):
    employeeid = models.IntegerField(primary_key=True)
    name = models.TextField(blank=True, null=True)
    type = models.TextField(blank=True, null=True)
    employmentstatus = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'employee'
