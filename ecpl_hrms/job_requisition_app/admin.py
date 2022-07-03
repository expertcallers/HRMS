from django.contrib import admin
from .models import *
from import_export import resources
from import_export.admin import ImportExportModelAdmin
# Register your models here

class ProfileSearch(admin.ModelAdmin):
    search_fields = ('emp_name','emp_id',"emp_desi")
    list_display = ('emp_name','emp_id', 'emp_desi','emp_process',"emp_rm1","emp_rm2","emp_rm3")
# class JobSearch(admin.ModelAdmin):
#     search_fields = ('req_raised_by','created_by_id')
#     list_display = ("id",'req_raised_by','created_by_id', 'requisition_date','hc_req',"initial_status","final_status","manager_approval")

class TicketSearch(admin.ModelAdmin):
    search_fields = ("job_requisition_id", 'created_by', 'created_by_id')
    list_display = ("job_requisition_id", 'created_by', 'created_by_id', 'created_date')

class CampaigntSearch(admin.ModelAdmin):
    search_fields = ("campaign_name", 'manager', 'manager_id')
    list_display = ("campaign_name", 'manager', 'manager_id')

class InterSearch(admin.ModelAdmin):
    search_fields = ('emp_name','emp_id')
    list_display = ('emp_name','emp_id')

admin.site.register(JobRequisition, JobSearch)
admin.site.register(Tickets, TicketSearch)

