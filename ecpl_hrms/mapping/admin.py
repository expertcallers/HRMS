from django.contrib import admin
from .models import *
from import_export import resources
from import_export.admin import ImportExportModelAdmin


# Register your models here.


class ProfileSearch(admin.ModelAdmin):
    search_fields = ('emp_name', 'emp_id', "emp_desi")
    list_display = ('emp_name', 'emp_id', 'emp_desi', 'emp_process', "emp_rm1", "emp_rm2", "emp_rm3")


class DataSearchResource(resources.ModelResource):
  class Meta:
     model = Data
     fields = ['emp_id', 'emp_name', 'emp_desi', 'emp_rm1_id', 'emp_rm2_id', 'emp_rm3_id', 'emp_process',
               "emp_rm1", "emp_rm2", "emp_rm3", 'emp_doj', 'emp_process_id']
     import_id_fields = ('emp_id',)

class DataSearch(ImportExportModelAdmin):
    search_fields = ('emp_name', 'emp_id', "emp_desi", 'emp_process')
    list_display = ('emp_name', 'emp_id', 'emp_desi', 'emp_process', "emp_rm1", "emp_rm2", "emp_rm3")
    resource_class = DataSearchResource


admin.site.register(Profile, ProfileSearch)
admin.site.register(MappingHistory)
admin.site.register(Data, DataSearch)
