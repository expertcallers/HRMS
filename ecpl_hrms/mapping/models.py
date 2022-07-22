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

class LoginHistory(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.PROTECT)
    date = models.DateField(null=True, blank=True)
    login = models.DateTimeField(null=True, blank=True)
    logout = models.DateTimeField(null=True, blank=True)
    done = models.BooleanField(default=False)

class EmpSeparation(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.PROTECT)
    date = models.DateField(null=True, blank=True)
    reason = models.TextField()
    rm1_approval = models.BooleanField(default=False, null=True, blank=True)
    rm1_comment = models.TextField(null=True, blank=True)
    rm2_approval = models.BooleanField(default=False, null=True, blank=True)
    rm2_comment = models.TextField(null=True, blank=True)
    rm3_approval = models.BooleanField(default=False, null=True, blank=True)
    rm3_comment = models.TextField(null=True, blank=True)
    admin = models.CharField(null=True, blank=True, max_length=200)
    admin_id = models.CharField(null=True, blank=True, max_length=30)
    admin_approval = models.BooleanField(default=False, null=True, blank=True)
    admin_comment = models.TextField(null=True, blank=True)
    hr = models.CharField(null=True, blank=True, max_length=200)
    hr_id = models.CharField(null=True, blank=True, max_length=30)
    hr_approval = models.BooleanField(default=False, null=True, blank=True)
    hr_comment = models.TextField(null=True, blank=True)
    last_working = models.DateField(null=True, blank=True)
    status = models.CharField(default='Applied', max_length=150)

class SOP(models.Model):
    created_by = models.CharField(max_length=200)
    created_id = models.CharField(max_length=30)
    created_date = models.DateTimeField()
    campaign_name = models.CharField(max_length=200)
    type = models.CharField(max_length=50)
    category = models.CharField(max_length=100)
    process_1 = models.CharField(max_length=100)
    process_2 = models.CharField(max_length=100)
    process_3 = models.CharField(max_length=100)
    report_format = models.TextField()
    other_info = models.TextField()
    status = models.CharField(max_length=50)

class SOPAgent(models.Model):
    sop = models.ForeignKey(SOP, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)

class SOPLeader(models.Model):
    sop = models.ForeignKey(SOP, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)

class SOPDataSource(models.Model):
    sop = models.ForeignKey(SOP, on_delete=models.CASCADE)
    source = models.CharField(max_length=50)
    location = models.TextField(null=True, blank=True)
    username = models.CharField(max_length=200)
    password = models.CharField(max_length=200)
