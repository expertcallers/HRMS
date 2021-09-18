from django.shortcuts import render
from .models import *
from calendar import Calendar, monthrange
c = Calendar()

# Create your views here.
def loginPage(request):
    return render(request,'ams/login.html')
def teamDashboard(request):
    return render(request, 'ams/team-dashboard.html')
def indexPage(request):

    team_name = 'Gubagoo'
    emp_team_obj = Employees.objects.filter(process = team_name)
    data = {'team':emp_team_obj}
    return render(request,'ams/index.html',data)

def employeeDetails(request,pk):
    emp_id = pk
    emp_obj = Employees.objects.get(emp_id = emp_id)
    data = {'employee':emp_obj}
    return render(request, 'ams/employee-details.html', data)

def markAttendance(request,pk):
    if request.method == 'POST':
        date_time = timezone.now()
        emp_id = 123
        emp_name = 'Test'
        process = 'Gubagoo'
        marked_by_id = 1000
        marked_by_name = 'Test TL'
        attendance_type = request.POST['leave_type']
        remarks = "Noneee"

        att = Attendace.objects.create(emp_id=emp_id,emp_name=emp_name,date_time=date_time,process=process,
                                      marked_by_id=marked_by_id,marked_by_name=marked_by_name,attendance_type=attendance_type,
                                      remarks=remarks)
        att.save()
        print("created")

    else:
        emp_id = pk
        for d in [x for x in c.itermonthdates(2019, 7) if x.month == 7]:
            print(d)

        return render(request,'ams/attendace-marking-form.html')

