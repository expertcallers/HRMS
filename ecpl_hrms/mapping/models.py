from statistics import mode
from django.contrib.auth.models import User
from django.db import models
import datetime

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    emp_id = models.CharField(max_length=100,null=True)
    emp_name = models.CharField(max_length=200)
    emp_desi = models.CharField(max_length=200)
    emp_rm1 = models.CharField(max_length=200)
    emp_rm1_id = models.CharField(max_length=10)
    emp_rm2 = models.CharField(max_length=200)
    emp_rm2_id = models.CharField(max_length=10)
    emp_rm3 = models.CharField(max_length=200)
    emp_rm3_id = models.CharField(max_length=10)
    emp_process = models.CharField(max_length=200)
    emp_process_id = models.CharField(max_length=10)
    pc = models.BooleanField(default=False)
    img = models.ImageField(upload_to='users/',default="users/default.png")
    doj = models.DateField(null=True,blank=True)
    active = models.BooleanField(default=True)
    on_id = models.IntegerField(null=True,blank=True)
    agent_status = models.CharField(max_length=20,default='Active')
    emp_email = models.EmailField(null=True, blank=True)
    otp = models.CharField(max_length=12, null=True, blank=True)
    otp_time = models.DateTimeField(null=True, blank=True)
    email_verify = models.BooleanField(default=False)

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
        return self.updated_by


class NewData(models.Model):
    emp_id = models.CharField(max_length=100, primary_key=True)
    emp_name = models.CharField(max_length=200)
    emp_desi = models.CharField(max_length=200)
    emp_rm1 = models.CharField(max_length=200)
    emp_rm1_id = models.CharField(max_length=10)
    emp_rm2 = models.CharField(max_length=200)
    emp_rm2_id = models.CharField(max_length=10)
    emp_rm3 = models.CharField(max_length=200)
    emp_rm3_id = models.CharField(max_length=10)
    emp_process = models.CharField(max_length=200)
    emp_process_id = models.CharField(max_length=10, null=True, blank=True)
    emp_doj = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.emp_name