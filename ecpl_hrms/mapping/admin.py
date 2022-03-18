from django.contrib import admin
from .models import *
# Register your models here.
class ProfileSearch(admin.ModelAdmin):
    search_fields = ('emp_name','emp_id',"emp_desi")
    list_display = ('emp_name','emp_id', 'emp_desi','emp_process',"emp_rm1","emp_rm2","emp_rm3")

admin.site.register(Profile,ProfileSearch)
admin.site.register(MappingHistory)
admin.site.register(Data)
