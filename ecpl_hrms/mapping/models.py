from django.contrib.auth.models import User
from django.db import models

# Create your models here.

class Employee(models.Model):
    emp_id = models.IntegerField()
    emp_name = models.CharField(max_length=200)
    emp_desi = models.CharField(max_length=200)
    emp_rm1 = models.CharField(max_length=200)
    emp_rm2 = models.CharField(max_length=200)
    emp_rm3 = models.CharField(max_length=200)
    emp_process = models.CharField(max_length=200)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    emp_id = models.IntegerField()
    emp_name = models.CharField(max_length=200)
    emp_desi = models.CharField(max_length=200)
    emp_rm1 = models.CharField(max_length=200)
    emp_rm2 = models.CharField(max_length=200)
    emp_rm3 = models.CharField(max_length=200)
    emp_process = models.CharField(max_length=200)

    def __str__(self):
        return self.emp_name


