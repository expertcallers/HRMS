from django.contrib import admin
from .models import *
from import_export import resources
from import_export.admin import ImportExportModelAdmin


# Register your models here.
class ProfileResource(resources.ModelResource):
  class Meta:
     model = Profile
     # fields = ['id', 'user', 'emp_id', 'emp_name', 'emp_desi', "emp_rm1", 'emp_rm1_id', "emp_rm2", 'emp_rm2_id',
     #           "emp_rm3", 'emp_rm3_id', 'emp_process', 'emp_process_id', 'doj']

class ProfileSearch(ImportExportModelAdmin):
    search_fields = ('emp_name', 'emp_id', "emp_desi", 'emp_process')
    list_display = ('emp_name', 'emp_id', 'emp_desi', 'emp_process', "emp_rm1", "emp_rm2", "emp_rm3",'agent_status')
    list_filter = ("agent_status",)
    resource_class = ProfileResource


class MappingSearch(admin.ModelAdmin):
    search_fields = ('emp_name', 'emp_id', "emp_desi")
    list_display = ('date','emp_name', 'emp_id', 'team', "rm1", "rm2", "rm3",'history')


class DataSearchResource(resources.ModelResource):
  class Meta:
     model = NewData
     fields = ['emp_id', 'emp_name', 'emp_desi', 'emp_rm1_id', 'emp_rm2_id', 'emp_rm3_id', 'emp_process',
               "emp_rm1", "emp_rm2", "emp_rm3", 'emp_doj', 'emp_process_id']
     import_id_fields = ('emp_id',)

class DataSearch(ImportExportModelAdmin):
    search_fields = ('emp_name', 'emp_id', "emp_desi", 'emp_process')
    list_display = ('emp_name', 'emp_id', 'emp_desi', 'emp_process', "emp_rm1", "emp_rm2", "emp_rm3")
    resource_class = DataSearchResource


admin.site.register(Profile, ProfileSearch)
admin.site.register(MappingHistory, MappingSearch)
admin.site.register(NewData, DataSearch)
