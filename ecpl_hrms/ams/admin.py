from django.contrib import admin
from .models import *
# Register your models here
class ProfileSearch(admin.ModelAdmin):
    search_fields = ('emp_name','emp_id',"att_actual")
    list_display = ('emp_name','emp_id',"date","att_actual")
    filter = ('emp_id',"date","att_actual")


admin.site.register(EcplCalander,ProfileSearch)
admin.site.register(OnboardingnewHRC)

admin.site.register(JobRequisition)
admin.site.register(Campaigns)

admin.site.register(EmployeeLeaveBalance)
admin.site.register(AgentActiveStatusHist)
admin.site.register(LeaveTable)
admin.site.register(AddAttendanceMonths)


