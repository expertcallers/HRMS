from django.contrib import admin
from .models import *
from import_export import resources
from import_export.admin import ImportExportModelAdmin
# Register your models here
class AttendanceResourse(resources.ModelResource):
  class Meta:
      model = EcplCalander


class AttendanceSearch(ImportExportModelAdmin):
    search_fields = ('emp_name','emp_id',"att_actual")
    list_display = ('emp_name','emp_id',"date","att_actual")
    list_filter = ("date","att_actual")
    resource_class = AttendanceResourse

class LeaveHistorySearch(admin.ModelAdmin):
    search_fields = ('emp_id','date')
    list_display = ('date','emp_id',"leave_type","transaction","no_days",'total')

class AddAttendanceMonthsSearch(admin.ModelAdmin):
    search_fields = ('month','year')
    list_display = ('month','month_number',"year","created", "leave",)

class DateStatus(admin.ModelAdmin):
    search_fields = ('date','status')
    list_display = ('date','status')

class MappingSearch(admin.ModelAdmin):
    search_fields = ('emp_name','emp_id')
    list_display = ('emp_name','emp_id','emp_desi','emp_rm1','emp_rm2','emp_rm3','new_rm1','new_rm2','new_rm3','emp_process','new_process','status')

class AgentActiveStatusHistSearch(admin.ModelAdmin):
    search_fields = ('emp_name','emp_id')
    list_display = ('emp_name','emp_id','current_status','new_status','date','changed_by','approved_by','ticket_status')

class AttendanceCorrectionHistorySearch(admin.ModelAdmin):
    search_fields = ('emp_name','emp_id')
    list_display = ('emp_name','emp_id','applied_by','date_for','att_old','att_new','reason','om_response','approved_by','status')

class LeaveTableSearch(admin.ModelAdmin):
    search_fields = ('emp_name','emp_id')
    list_display = ('emp_name','emp_id','applied_date','leave_type','start_date','end_date','no_days','tl_approval','manager_approval', 'escalation', 'status')
    list_filter = ('tl_approval','manager_approval', 'escalation', 'status')

class OnboardingnewHRCResourse(resources.ModelResource):
  class Meta:
      model = OnboardingnewHRC
      fields =['emp_id', 'emp_name', 'emp_dob', 'emp_desig', 'emp_process', 'emp_pan', 'emp_aadhar', 'emp_father_name',
               'emp_marital_status', 'emp_email', 'emp_phone', 'emp_alt_phone', 'emp_present_address',
               'emp_permanent_address', 'emp_blood', 'emp_emergency_person', 'emp_emergency_number',
               'emp_emergency_address', 'emp_emergency_person_two', 'emp_emergency_number_two',
               'emp_emergency_address_two', 'emp_edu_qualification', 'emp_quali_other', 'emp_edu_course',
               'emp_edu_institute', 'emp_pre_exp', 'emp_pre_industry', 'emp_pre_org_name', 'emp_pre_desg',
               'emp_pre_period_of_employment_frm', 'emp_pre_period_of_employment_to', 'emp_pre_exp_two',
               'emp_pre_industry_two', 'emp_pre_org_name_two', 'emp_pre_desg_two',
               'emp_pre_period_of_employment_frm_two', 'emp_pre_period_of_employment_to_two', 'emp_pre_exp_three',
               'emp_pre_industry_three', 'emp_pre_org_name_three', 'emp_pre_desg_three',
               'emp_pre_period_of_employment_frm_three', 'emp_pre_period_of_employment_to_three',
               'emp_bank_holder_name', 'emp_bank_name', 'emp_bank_acco_no', 'emp_bank_ifsc', 'have_system',
               'require_system', 'wifi_broadband', 'esic', 'pf', 'tds', 'pt']
      import_id_fields = ('emp_id',)
      clean_model_instances = True

class OnboardingnewHRCSearch(ImportExportModelAdmin):
    search_fields = ('emp_name','emp_id','emp_aadhar','emp_phone')
    list_display = ('emp_name','emp_id','emp_desig','emp_aadhar','emp_phone','hr_name')
    list_filter = ('user_created',)
    resource_class = OnboardingnewHRCResourse

class LeaveSearchResource(resources.ModelResource):
  class Meta:
      model = EmployeeLeaveBalance
      fields = ['emp_id', 'emp_name', "team", "pl_balance", "sl_balance"]
      import_id_fields = ('emp_id',)

class LeaveSearch(ImportExportModelAdmin):
    search_fields = ('emp_name','emp_id')
    list_display = ('emp_name','emp_id',"team","pl_balance","sl_balance")
    resource_class = LeaveSearchResource

class CampainSearchResource(resources.ModelResource):
  class Meta:
     model = Campaigns
     fields = ['id', 'name', 'om']

class CampaignSearch(ImportExportModelAdmin):
    search_fields = ('id', 'name', 'om')
    list_display = ('id', 'name', 'om')
    resource_class = CampainSearchResource

class DesignationSearchResource(resources.ModelResource):
  class Meta:
     model = Designation
     fields = ['id', 'name', 'category','created_by']

class DesignationSearch(ImportExportModelAdmin):
    search_fields = ('id', 'name', 'category')
    list_display = ('id', 'name', 'category','created_by')
    resource_class = DesignationSearchResource

class BillAdministrationSearch(admin.ModelAdmin):
    search_fields = ('po_no',)
    list_display = ('po_no', 'date', 'supplier', 'contact_person', 'grand_total')
    list_filter = ('supplier', 'contact_person')


class ItemDescriptionAdministrationSearch(admin.ModelAdmin):
    search_fields = ('bill',)
    list_display = ('bill', 'description', 'qty', 'gst_percent', 'amount')


class SupplierAdministrationSearch(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ('name', 'cantact_person', 'contact_no', 'contact_email')

class AccessControlSearch(admin.ModelAdmin):
    search_fields = ('emp_id', 'access')
    list_display = ('emp_id', 'access')
    list_filter = ('emp_id', 'access')


admin.site.register(EcplCalander, AttendanceSearch)
admin.site.register(OnboardingnewHRC, OnboardingnewHRCSearch)
admin.site.register(Campaigns, CampaignSearch)
admin.site.register(EmployeeLeaveBalance, LeaveSearch)
admin.site.register(AgentActiveStatusHist, AgentActiveStatusHistSearch)
admin.site.register(LeaveTable, LeaveTableSearch)
admin.site.register(AddAttendanceMonths, AddAttendanceMonthsSearch)
admin.site.register(leaveHistory, LeaveHistorySearch)
admin.site.register(DaysForAttendance, DateStatus)
admin.site.register(AttendanceCorrectionHistory, AttendanceCorrectionHistorySearch)
admin.site.register(MappingTickets, MappingSearch)
admin.site.register(LastEmpId)
admin.site.register(NoticeECPL)
admin.site.register(FaqHRMS)
admin.site.register(Designation, DesignationSearch)
admin.site.register(BillAdministration, BillAdministrationSearch)
admin.site.register(ItemDescriptionAdministration, ItemDescriptionAdministrationSearch)
admin.site.register(SupplierAdministration, SupplierAdministrationSearch)
admin.site.register(AccessControl, AccessControlSearch)


