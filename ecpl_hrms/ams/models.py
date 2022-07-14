from datetime import datetime, date
from statistics import mode

from django.contrib.auth.models import User
from django.db import models


# Attendance - Master ++

class EcplCalander(models.Model):
    unique_id = models.CharField(max_length=150, null=True, blank=True)
    team = models.CharField(max_length=300)
    date = models.DateField()
    emp_name = models.CharField(max_length=300)
    emp_id = models.CharField(max_length=50, null=True)
    emp_desi = models.CharField(max_length=100, null=True)
    att_actual = models.CharField(max_length=50, null=True)
    approved_on = models.DateTimeField(null=True)
    appoved_by = models.CharField(max_length=300, null=True)
    rm1 = models.CharField(max_length=200, null=True)
    rm2 = models.CharField(max_length=200, null=True)
    rm3 = models.CharField(max_length=200, null=True)
    rm1_id = models.CharField(max_length=30, null=True)
    rm2_id = models.CharField(max_length=30, null=True)
    rm3_id = models.CharField(max_length=30, null=True)
    team_id = models.IntegerField(null=True, blank=True)


# Onboarding - Master +
class OnboardingnewHRC(models.Model):
    unique_id = models.CharField(max_length=150, null=True, blank=True)
    hr_name = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hrname', null=True, blank=True)
    submit_date = models.DateTimeField(default=datetime.now())
    emp_id = models.CharField(max_length=50, null=True, blank=True)
    emp_name = models.CharField(max_length=300, null=True, blank=True)
    emp_dob = models.DateField(max_length=300, null=True, blank=True)
    emp_desig = models.CharField(max_length=300, null=True, blank=True)
    emp_process = models.CharField(max_length=300, null=True, blank=True)
    emp_pan = models.CharField(max_length=300, null=True, blank=True)
    emp_aadhar = models.CharField(max_length=300, null=True, blank=True)
    emp_father_name = models.CharField(max_length=300, null=True, blank=True)
    emp_marital_status = models.CharField(max_length=300, null=True, blank=True)
    emp_email = models.CharField(null=True, blank=True, max_length=300)
    emp_phone = models.CharField(max_length=300, null=True, blank=True)
    emp_alt_phone = models.CharField(max_length=300, null=True, blank=True)
    emp_present_address = models.CharField(max_length=500, null=True, blank=True)
    emp_permanent_address = models.CharField(max_length=500, null=True, blank=True)
    emp_blood = models.CharField(max_length=50, null=True, blank=True)
    emp_emergency_person = models.CharField(max_length=300, null=True, blank=True)
    emp_emergency_number = models.CharField(max_length=300, null=True, blank=True)
    emp_emergency_address = models.CharField(max_length=500, null=True, blank=True)
    emp_emergency_person_two = models.CharField(max_length=300, null=True, blank=True)
    emp_emergency_number_two = models.CharField(max_length=300, null=True, blank=True)
    emp_emergency_address_two = models.CharField(max_length=500, null=True, blank=True)
    emp_edu_qualification = models.CharField(max_length=300, null=True, blank=True)
    emp_quali_other = models.CharField(null=True, max_length=300, blank=True)
    emp_edu_course = models.CharField(null=True, max_length=300, blank=True)
    emp_edu_institute = models.CharField(max_length=300, null=True, blank=True)
    emp_pre_exp = models.CharField(null=True, blank=True, default=0, max_length=300)
    emp_pre_industry = models.CharField(max_length=300, null=True, blank=True)
    emp_pre_org_name = models.CharField(max_length=300, null=True, blank=True)
    emp_pre_desg = models.CharField(max_length=300, null=True, blank=True)
    emp_pre_period_of_employment_frm = models.CharField(null=True, blank=True, max_length=300)
    emp_pre_period_of_employment_to = models.CharField(null=True, blank=True, max_length=300)
    emp_pre_exp_two = models.CharField(null=True, blank=True, default=0, max_length=300)
    emp_pre_industry_two = models.CharField(max_length=300, null=True, blank=True)
    emp_pre_org_name_two = models.CharField(max_length=300, null=True, blank=True)
    emp_pre_desg_two = models.CharField(max_length=300, null=True, blank=True)
    emp_pre_period_of_employment_frm_two = models.CharField(null=True, blank=True, max_length=300)
    emp_pre_period_of_employment_to_two = models.CharField(null=True, blank=True, max_length=300)
    emp_pre_exp_three = models.CharField(null=True, blank=True, default=0, max_length=300)
    emp_pre_industry_three = models.CharField(max_length=300, null=True, blank=True)
    emp_pre_org_name_three = models.CharField(max_length=300, null=True, blank=True)
    emp_pre_desg_three = models.CharField(max_length=300, null=True, blank=True)
    emp_pre_period_of_employment_frm_three = models.CharField(null=True, blank=True, max_length=300)
    emp_pre_period_of_employment_to_three = models.CharField(null=True, blank=True, max_length=300)
    emp_bank_holder_name = models.CharField(max_length=300, null=True, blank=True)
    emp_bank_name = models.CharField(max_length=300, null=True, blank=True)
    emp_bank_acco_no = models.CharField(max_length=50, null=True, blank=True)
    emp_bank_ifsc = models.CharField(max_length=20, null=True, blank=True)
    have_system = models.CharField(null=True, max_length=50, blank=True)
    require_system = models.CharField(null=True, max_length=50, blank=True)
    wifi_broadband = models.CharField(null=True, max_length=50, blank=True)
    emp_upload_aadhar = models.ImageField(upload_to='Aadhar/', null=True, blank=True)
    emp_upload_aadhar_back = models.ImageField(upload_to='Aadhar/', null=True, blank=True)
    emp_upload_pan = models.ImageField(upload_to='Pan/', null=True, blank=True)
    emp_upload_id = models.ImageField(upload_to='Id/', null=True, blank=True)
    emp_upload_id_back = models.ImageField(upload_to='Id/', null=True, blank=True)
    emp_upload_edu_sslc = models.ImageField(upload_to='Certificate/', null=True, blank=True)
    emp_upload_edu_twelveth = models.ImageField(upload_to='Certificate/', null=True, blank=True)
    emp_upload_edu_gradu = models.ImageField(upload_to='Certificate/', null=True, blank=True)
    emp_upload_experience = models.ImageField(upload_to='Experience/', null=True, blank=True)
    emp_upload_experience_two = models.ImageField(upload_to='Experience/', null=True, blank=True)
    emp_upload_experience_three = models.ImageField(upload_to='Experience/', null=True, blank=True)
    emp_upload_bank = models.ImageField(upload_to='Passbook/', null=True, blank=True)
    esic = models.CharField(max_length=50, null=True, blank=True)
    pf = models.CharField(max_length=50, null=True, blank=True)
    tds = models.CharField(max_length=50, null=True, blank=True)
    pt = models.CharField(max_length=50, null=True, blank=True)
    user_created = models.BooleanField(default=False)


# Mapping Tickets - request - approval ++
class MappingTickets(models.Model):
    unique_id = models.CharField(max_length=150, null=True, blank=True)
    emp_name = models.CharField(max_length=50)
    emp_id = models.CharField(max_length=10)
    emp_desi = models.CharField(max_length=50)
    emp_rm1 = models.CharField(max_length=50)
    emp_rm2 = models.CharField(max_length=50)
    emp_rm3 = models.CharField(max_length=50)
    emp_rm1_id = models.CharField(max_length=50, null=True, blank=True)
    emp_rm2_id = models.CharField(max_length=50, null=True, blank=True)
    emp_rm3_id = models.CharField(max_length=50, null=True, blank=True)
    new_rm1 = models.CharField(max_length=50)
    new_rm2 = models.CharField(max_length=50)
    new_rm3 = models.CharField(max_length=50)
    new_rm1_id = models.CharField(max_length=50, null=True, blank=True)
    new_rm2_id = models.CharField(max_length=50, null=True, blank=True)
    new_rm3_id = models.CharField(max_length=50, null=True, blank=True)
    emp_process = models.CharField(max_length=50)
    new_process = models.CharField(max_length=50)
    created_by = models.CharField(max_length=50)
    created_by_id = models.CharField(max_length=50)
    created_date = models.DateTimeField()
    effective_date = models.DateField()
    approved_by = models.TextField(null=True, blank=True)
    approved_date = models.DateTimeField(null=True, blank=True)
    status = models.BooleanField(default=False)
    action = models.CharField(max_length=50, null=True, blank=True)
    reason = models.TextField(null=True, blank=True)


# Campaigns - teams +
class Campaigns(models.Model):
    unique_id = models.CharField(max_length=150, null=True, blank=True)
    name = models.CharField(max_length=100)
    om = models.CharField(max_length=50, null=True, blank=True)
    created_by = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.name


# Leave Balance - PL - SL +
class EmployeeLeaveBalance(models.Model):
    unique_id = models.CharField(max_length=150, null=True, blank=True)
    emp_id = models.CharField(max_length=10, null=True)
    emp_name = models.CharField(max_length=50, null=True)
    team = models.CharField(max_length=50, null=True)
    pl_balance = models.FloatField()
    sl_balance = models.FloatField()
    present_count = models.IntegerField(default=0)


# Leave apply - save - approval ++
class LeaveTable(models.Model):
    unique_id = models.CharField(max_length=150, null=True, blank=True)
    emp_name = models.CharField(max_length=50, null=True)
    emp_id = models.CharField(max_length=50, null=True)
    emp_desi = models.CharField(max_length=50, null=True)
    emp_process = models.CharField(max_length=50, null=True)
    leave_type = models.CharField(max_length=50, null=True)
    applied_date = models.DateTimeField(null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    no_days = models.IntegerField()
    agent_reason = models.TextField(null=True)
    tl_approval = models.BooleanField(default=False)
    tl_date = models.DateTimeField(null=True, blank=True)
    tl_status = models.CharField(max_length=50, null=True, blank=True)
    tl_reason = models.TextField(null=True)
    status = models.CharField(max_length=50, null=True)
    manager_approval = models.BooleanField(default=False)
    manager_date = models.DateTimeField(null=True, blank=True)
    manager_reason = models.TextField(null=True)
    manager_status = models.CharField(max_length=50, null=True, blank=True)
    emp_rm1 = models.CharField(max_length=50, null=True)
    emp_rm2 = models.CharField(max_length=50, null=True)
    emp_rm3 = models.CharField(max_length=50, null=True)
    emp_rm1_id = models.CharField(max_length=50, null=True)
    emp_rm2_id = models.CharField(max_length=50, null=True)
    emp_rm3_id = models.CharField(max_length=50, null=True)
    escalation = models.BooleanField(default=False)
    escalation_reason = models.TextField(null=True)
    proof = models.FileField(null=True, blank=True, upload_to='Uploads/SL_Proof')


# Attendance correction history - send - approve ++
# class AttendanceCorrectionHistory(models.Model):
#     unique_id = models.CharField(max_length=150, null=True, blank=True)
#     applied_by = models.CharField(max_length=30, null=True, blank=True)
#     applied_by_id = models.CharField(max_length=30, null=True, blank=True)
#     applied_date = models.DateField()
#     date_for = models.DateField()
#     att_old = models.CharField(max_length=30, null=True, blank=True)
#     att_new = models.CharField(max_length=30, null=True, blank=True)
#     emp_name = models.CharField(max_length=30, null=True, blank=True)
#     emp_id = models.CharField(max_length=30, null=True, blank=True)
#     rm3_name = models.CharField(max_length=50)
#     rm3_id = models.CharField(max_length=50)
#     approved_by = models.CharField(max_length=30, null=True, blank=True)
#     approved_on = models.DateTimeField(null=True, blank=True)
#     status = models.BooleanField(default=False)
#     cal_id = models.IntegerField()
#     om_response = models.CharField(max_length=150, default='Pending by OM')
#     comments = models.TextField(null=True, blank=True)
#     reason = models.TextField(null=True, blank=True)


# Agent status change history - att - ben - training +
class AgentActiveStatusHist(models.Model):
    unique_id = models.CharField(max_length=150, null=True, blank=True)
    emp_id = models.CharField(max_length=20, null=True, blank=True)
    emp_name = models.CharField(max_length=30, null=True, blank=True)
    current_status = models.CharField(max_length=20, null=True, blank=True)
    new_status = models.CharField(max_length=20, null=True, blank=True)
    date = models.DateField()
    reason = models.TextField()
    changed_by = models.CharField(max_length=30)
    approved_by = models.CharField(max_length=50)
    hr_response = models.TextField(null=True, blank=True)
    status_by_hr = models.CharField(max_length=50)
    ticket_status = models.BooleanField(default=False)


class AddAttendanceMonths(models.Model):
    unique_id = models.CharField(max_length=150, null=True, blank=True)
    month = models.CharField(max_length=30)
    month_number = models.IntegerField()
    year = models.IntegerField()
    created = models.BooleanField(default=False)
    created_by = models.CharField(max_length=150, null=True, blank=True)
    leave = models.BooleanField(default=False)
    leave_by = models.CharField(max_length=150, null=True, blank=True)


class leaveHistory(models.Model):
    unique_id = models.CharField(max_length=150, null=True, blank=True)
    emp_id = models.CharField(max_length=30)
    date = models.DateField()
    leave_type = models.CharField(max_length=30)
    transaction = models.CharField(max_length=300)
    no_days = models.FloatField()
    total = models.FloatField(null=True, blank=True)


class DaysForAttendance(models.Model):
    date = models.DateField()
    status = models.BooleanField(default=False)


class LastEmpId(models.Model):
    emp_id = models.CharField(max_length=30)

    def __str__(self):
        return self.emp_id


class Designation(models.Model):
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=200, null=True, blank=True)
    created_by = models.CharField(max_length=200, default="CC Team")


class NoticeECPL(models.Model):
    note = models.TextField()

    def __str__(self):
        return str(self.id) + ' - ' + self.note


class FaqHRMS(models.Model):
    question = models.TextField()
    answer = models.TextField()

    def __str__(self):
        return self.question


class SupplierAdministration(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField()
    cantact_person = models.CharField(max_length=200)
    contact_no = models.CharField(max_length=50)
    contact_email = models.CharField(max_length=200)
    pan = models.CharField(max_length=200)
    gst = models.CharField(max_length=200)
    acc_name = models.CharField(max_length=200)
    acc_no = models.CharField(max_length=200)
    bank_name = models.CharField(max_length=200)
    bank_branch = models.CharField(max_length=200)
    ifsc = models.CharField(max_length=200)
    cin_code = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.name


class BillAdministration(models.Model):
    project = models.CharField(max_length=200)
    po_no = models.CharField(max_length=50)
    date = models.DateField()
    billing_office = models.CharField(max_length=200, null=True, blank=True)
    category = models.CharField(max_length=200, null=True, blank=True)
    delivery_office = models.CharField(max_length=200)
    delivery_address = models.TextField()
    contact_person = models.CharField(max_length=200)
    contact_no = models.CharField(max_length=50)
    contact_email = models.EmailField()
    terms_conditions = models.TextField()
    amount_words = models.TextField(null=True, blank=True)
    pan = models.CharField(max_length=200, default='AAECE0810D')
    gst = models.CharField(max_length=200, default='29AAECE0810D1Z6')
    total_amount = models.FloatField(null=True, blank=True)
    gst_amount = models.FloatField(null=True, blank=True)
    grand_total = models.FloatField(null=True, blank=True)

    supplier = models.CharField(max_length=200, null=True, blank=True)
    supplier_address = models.TextField(null=True, blank=True)
    supplier_contact_person = models.CharField(max_length=200, null=True, blank=True)
    supplier_contact_no = models.CharField(max_length=50, null=True, blank=True)
    supplier_contact_email = models.CharField(max_length=200, null=True, blank=True)
    supplier_pan = models.CharField(max_length=200, null=True, blank=True)
    supplier_gst = models.CharField(max_length=200, null=True, blank=True)
    acc_name = models.CharField(max_length=200, null=True, blank=True)
    acc_no = models.CharField(max_length=200, null=True, blank=True)
    bank_name = models.CharField(max_length=200, null=True, blank=True)
    bank_branch = models.CharField(max_length=200, null=True, blank=True)
    ifsc = models.CharField(max_length=200, null=True, blank=True)
    cin_code = models.CharField(max_length=200, null=True, blank=True)


class ItemDescriptionAdministration(models.Model):
    bill = models.ForeignKey(BillAdministration, on_delete=models.CASCADE)
    description = models.TextField()
    qty = models.IntegerField()
    gst_percent = models.IntegerField(null=True, blank=True)
    gst_amount = models.FloatField(null=True, blank=True)
    price = models.FloatField()
    amount = models.FloatField()


class AccessControl(models.Model):
    emp_id = models.CharField(max_length=30)
    access = models.CharField(max_length=200)
