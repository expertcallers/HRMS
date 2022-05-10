from django.contrib import admin
from .models import *
from import_export import resources
from import_export.admin import ImportExportModelAdmin
# Register your models here
class AttendanceSearch(admin.ModelAdmin):
    search_fields = ('emp_name','emp_id',"att_actual")
    list_display = ('emp_name','emp_id',"date","att_actual")
    filter = ('emp_id',"date","att_actual")

class LeaveSearchResource(resources.ModelResource):
  class Meta:
      model = EmployeeLeaveBalance
      fields = ['emp_id', 'emp_name', "team", "pl_balance", "sl_balance"]
      import_id_fields = ('emp_id',)

class LeaveSearch(ImportExportModelAdmin):
    search_fields = ('emp_name','emp_id')
    list_display = ('emp_name','emp_id',"team","pl_balance","sl_balance")
    resource_class = LeaveSearchResource

class LeaveHistorySearch(admin.ModelAdmin):
    search_fields = ('emp_id','date')
    list_display = ('date','emp_id',"leave_type","transaction","no_days",'total')
    filter = ('emp_id',"date")

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

class OnboardingnewHRCSearch(admin.ModelAdmin):
    search_fields = ('emp_name','emp_aadhar','emp_phone')
    list_display = ('submit_date','emp_name','emp_desig','emp_aadhar','emp_phone','hr_name','user_created')

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
admin.site.register(Designation, DesignationSearch)

