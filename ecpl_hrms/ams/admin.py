from django.contrib import admin
from .models import *
# Register your models here
class AttendanceSearch(admin.ModelAdmin):
    search_fields = ('emp_name','emp_id',"att_actual")
    list_display = ('emp_name','emp_id',"date","att_actual")
    filter = ('emp_id',"date","att_actual")

class LeaveSearch(admin.ModelAdmin):
    search_fields = ('emp_name','emp_id')
    list_display = ('emp_name','emp_id',"team","pl_balance","sl_balance","present_count")

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


admin.site.register(EcplCalander, AttendanceSearch)
admin.site.register(OnboardingnewHRC)
admin.site.register(Campaigns)
admin.site.register(EmployeeLeaveBalance, LeaveSearch)
admin.site.register(AgentActiveStatusHist)
admin.site.register(LeaveTable)
admin.site.register(AddAttendanceMonths, AddAttendanceMonthsSearch)
admin.site.register(leaveHistory, LeaveHistorySearch)
admin.site.register(DaysForAttendance,DateStatus)
admin.site.register(AttendanceCorrectionHistory)
admin.site.register(MappingTickets, MappingSearch)
admin.site.register(LastEmpId)

