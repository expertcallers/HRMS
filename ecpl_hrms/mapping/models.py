from django.contrib.auth.models import User
from django.db import models
import datetime

# Create your models here.

class Employee(models.Model):
    emp_id = models.CharField(max_length=200,null=True)
    emp_name = models.CharField(max_length=200)
    emp_desi = models.CharField(max_length=200)
    emp_rm1 = models.CharField(max_length=200)
    emp_rm2 = models.CharField(max_length=200)
    emp_rm3 = models.CharField(max_length=200)
    emp_process = models.CharField(max_length=200)
    id_extra = models.IntegerField(null=True)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    emp_id = models.IntegerField()
    emp_name = models.CharField(max_length=200)
    emp_desi = models.CharField(max_length=200)
    emp_rm1 = models.CharField(max_length=200)
    emp_rm2 = models.CharField(max_length=200)
    emp_rm3 = models.CharField(max_length=200)
    emp_process = models.CharField(max_length=200)
    extra_id = models.IntegerField(default=1)
    pc = models.BooleanField(default=False)

    def __str__(self):
        return self.emp_name


class MappingHistory(models.Model):
    date = models.DateField(default=datetime.date.today)
    updated_by = models.CharField(max_length=50)
    emp_name = models.CharField(max_length=50,null=True)
    emp_id = models.IntegerField(null=True)
    rm1 = models.CharField(max_length=50,null=True)
    rm2 = models.CharField(max_length=50, null=True)
    rm3 = models.CharField(max_length=50, null=True)
    team = models.CharField(max_length=100,null=True)
    history = models.CharField(max_length=200,null=True)

    def __str__(self):
        return self.date


class MappingHistoryTeam(models.Model):
    date = models.DateField(default=datetime.date.today)
    updated_by = models.CharField(max_length=50)
    team = models.CharField(max_length=100, null=True)
    category = models.CharField(max_length=50)
    new_value = models.CharField(max_length=100)

    def __str__(self):
        return self.date



