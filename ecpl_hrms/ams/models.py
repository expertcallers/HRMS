from django.contrib.auth.models import User
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
    att_actual = models.CharField(max_length=50,null=True)
    approved_on = models.DateTimeField(null=True)
    appoved_by = models.CharField(max_length=300,null=True)
    applied_status = models.BooleanField(default=False)
    rm1 = models.CharField(max_length=200,null=True)
    rm2 = models.CharField(max_length=200, null=True)
    rm3 = models.CharField(max_length=200, null=True)


class Onboarding(models.Model):

    emp_name=models.CharField(max_length=50)
    emp_dob=models.DateField(null=True,blank=True)
    emp_desi=models.CharField(max_length=50)
    emp_process=models.CharField(max_length=50)
    emp_pan=models.CharField(max_length=50)
    emp_aadhar=models.IntegerField(null=True,blank=True)
    emp_father_name=models.CharField(max_length=50)
    emp_marital_status=models.CharField(max_length=50)
    emp_email=models.EmailField(null=True,blank=True)
    emp_phone=models.IntegerField(null=True,blank=True)
    emp_alt_phone=models.IntegerField(null=True,blank=True)
    emp_present_address=models.CharField(max_length=500)
    emp_permanent_address=models.CharField(max_length=500)
    emp_blood_group=models.CharField(max_length=100)
    emp_emergency_person=models.CharField(max_length=50)
    emp_emergency_number=models.IntegerField(null=True,blank=True)
    emp_emergency_address=models.CharField(max_length=500)
    emp_edu_quali=models.CharField(max_length=100)
    emp_edu_course=models.CharField(max_length=100)
    emp_edu_institute=models.CharField(max_length=200)
    emp_pre_exp=models.CharField(max_length=100)
    emp_pre_industry=models.CharField(max_length=100)
    emp_pre_org_name=models.CharField(max_length=150)
    emp_pre_desi=models.CharField(max_length=100)
    emp_prev_tenure=models.CharField(max_length=100)
    emp_bank_name=models.CharField(max_length=100)
    emp_account_no=models.IntegerField(null=True,blank=True)
    emp_bank_ifsc=models.CharField(max_length=50)
    emp_aadhar=models.ImageField(upload_to='Aadhar/')
    emp_pan=models.ImageField(upload_to='Pan/')
    emp_idcard=models.ImageField(upload_to='Id/')
    emp_certificate=models.ImageField(upload_to='Certificate/')
    emp_exp_letter=models.ImageField(upload_to='Experience/')
    emp_passbook=models.ImageField(upload_to='Passbook/')

    added_by = models.CharField(max_length=100,null=True,blank=True)

class MappingTickets(models.Model):
    emp_name=models.CharField(max_length=50)
    emp_id = models.CharField(max_length=10)
    emp_desi = models.CharField(max_length=50)
    emp_rm1 = models.CharField(max_length=50)
    emp_rm2 = models.CharField(max_length=50)
    emp_rm3 = models.CharField(max_length=50)
    new_rm1 = models.CharField(max_length=50)
    new_rm2 = models.CharField(max_length=50)
    new_rm3 = models.CharField(max_length=50)
    emp_process = models.CharField(max_length=50)
    new_process = models.CharField(max_length=50)
    created_by=models.TextField()
    created_date=models.DateTimeField()
    effective_date=models.DateField()
    approved_by=models.TextField(null=True,blank=True)
    approved_date=models.DateTimeField(null=True,blank=True)
    status=models.BooleanField(default=False)


class Campaigns(models.Model):
    name=models.CharField(max_length=100)
    om = models.CharField(max_length=50)
    created_by = models.CharField(max_length=50,null=True,blank=True)
    created_date = models.DateField(null=True,blank=True)

class JobRequisition(models.Model):
    user_name = models.ForeignKey(User,on_delete=models.CASCADE,related_name='log_user',null=True)
    req_date = models.DateField()
    hc_req = models.TextField()
    req_raised_by = models.TextField()
    position = models.TextField()
    department = models.CharField(max_length=50, null=True)
    designation = models.TextField()
    process_typ_one = models.TextField()
    process_typ_two = models.TextField()
    process_typ_three = models.TextField()
    salary_rang_frm = models.IntegerField()
    salary_rang_to = models.IntegerField()
    qualification = models.TextField()
    other_quali = models.TextField()
    skills_set = models.TextField()
    languages = models.TextField()
    shift_timing = models.TextField()
    working_from = models.TextField()
    working_to = models.TextField()
    # week_off = models.TextField()
    # week_no_days = models.IntegerField()
    # week_from = models.TextField()
    # week_two = models.TextField()
    requisition_typ = models.TextField()
    candidate_name = models.TextField()
    closure_date = models.DateField()
    source = models.TextField()
    source_empref_emp_name = models.TextField()
    source_empref_emp_id = models.CharField(max_length=20)
    source_social = models.CharField(max_length=100, null=True, blank=True)
    source_partners = models.TextField()

