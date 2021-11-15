from django.db import models
from django.utils import timezone


# Create your models here.
class Employees(models.Model):
    emp_id = models.IntegerField(unique=True)
    emp_name = models.CharField(max_length=200)
    emp_desi = models.CharField(max_length=200)
    rm1 = models.CharField(max_length=200)
    rm2 = models.CharField(max_length=200)
    rm3 = models.CharField(max_length=200)
    process = models.CharField(max_length=300)

class Attendace(models.Model):
    emp_id = models.IntegerField(unique=True)
    emp_name = models.CharField(max_length=300)
    date_time = models.DateTimeField(default=timezone.now)
    process = models.CharField(max_length=300)
    marked_by_id = models.IntegerField()
    marked_by_name = models.CharField(max_length=300)
    attendance_type = models.CharField(max_length=100,default="Unmarked")
    remarks = models.TextField()

class EcplCalander(models.Model):
    team = models.CharField(max_length=300)
    date = models.DateField()
    emp_name = models.CharField(max_length=300)
    emp_id = models.CharField(max_length=50,null=True)
    emp_desi = models.CharField(max_length=100,null=True)
    att_applied = models.CharField(max_length=100)
    att_approved = models.CharField(max_length=100,null=True)
    att_actual = models.CharField(max_length=50,null=True)
    applied_on = models.DateTimeField(null=True)
    approved_on = models.DateTimeField(null=True)
    applied_by = models.CharField(max_length=300)
    appoved_by = models.CharField(max_length=300,null=True)
    approved_status = models.BooleanField(default=False)
    applied_status = models.BooleanField(default=False)
    rm1 = models.CharField(max_length=200,null=True)
    rm2 = models.CharField(max_length=200, null=True)
    rm3 = models.CharField(max_length=200, null=True)



