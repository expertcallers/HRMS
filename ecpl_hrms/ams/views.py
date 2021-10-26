from datetime import datetime

from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.shortcuts import render, redirect
from .models import *
from calendar import Calendar, monthrange
from django.contrib import messages
from django.apps import apps
Employee = apps.get_model('mapping', 'Employee')

c = Calendar()
from datetime import date
from django.db.models import Q



# Create your views here.
def loginPage(request):
    form = AuthenticationForm()
    teams = Employee.objects.values_list('emp_process', flat=True).distinct()
    data = {'teams':teams,'form':form}
    return render(request,'ams/login.html',data)

def loginAndRedirect(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)  # Login form
        team = request.POST['team']
        if form.is_valid():
            # login the user
            user = form.get_user()
            login(request, user)

            if request.user.profile.pc == False:
                return redirect('/ams/change-password')

            if team != request.user.profile.emp_process:
                logout(request)
                messages.info(request,'Invalid Team')
                return redirect('/ams')
            if request.user.profile.emp_desi == 'Team Leader - GB':
                return redirect('/ams/tl-dashboard')
            else:
                return redirect('/ams/agent-dashboard')
        else:
            form = AuthenticationForm()
            messages.info(request,'Invalid Credentials')
            teams = Employee.objects.values_list('emp_process', flat=True).distinct()
            data = {'teams': teams, 'form': form}
            return render(request, 'ams/login.html', data)


def logoutView(request):
    logout(request)
    return redirect('/ams')

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')

            user = request.user
            user.profile.pc = True
            user.save()
            user.profile.save()
            logout(request)
            return redirect('/ams')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request,'ams/change-password.html', {'form': form})


def teamDashboard(request):
    return render(request,'ams/team-dashboard.html')

def agentDashBoard(request):
    today = date.today()
    #today = '2021-9-28'
    emp_name = request.user.profile.emp_name
    emp_id = request.user.profile.emp_id
    emp = Employee.objects.get(emp_id = emp_id)
    try:
        cal_day = EcplCalander.objects.get(date=today,applied_status=True,emp_id=emp_id)
        today = 'Applied'
    except EcplCalander.DoesNotExist:
        today = str(today)

    #attendance status
    cal = EcplCalander.objects.filter(emp_id=emp_id).order_by('-date')[:3]
    data = {'emp_name':emp_name,'emp':emp,'date':today,'cal':cal}
    return render(request,'ams/agent-dashboard.html',data)

def tlDashboard(request):
    emp_name = request.user.profile.emp_name
    emp_id = request.user.profile.emp_id
    emp = Employee.objects.get(emp_id=emp_id)
    cal = EcplCalander.objects.filter(approved_status=False,rm1=emp_name)

    # details
    today = date.today()
    today = str(today)
    att_details = EcplCalander.objects.filter(date = today,rm1=emp_name)
    all_active = Employee.objects.filter(emp_rm1=emp_name).order_by('emp_name')
    all_present = EcplCalander.objects.filter(Q(rm1=emp_name) ,Q(date=today),Q(applied_status=True),Q(att_approved='approved'),Q(att_applied='present') |
                               Q(att_applied='Hald Day')).order_by('emp_name')

    #Unmarked Employees
    emps = Employee.objects.filter(emp_rm1=emp_name)
    unmarked_emps = []
    for i in emps:
        um = EcplCalander.objects.filter(emp_id = i.emp_id,date = today,applied_status=True)
        if um:
            pass
        else:
            unmarked_emps.append(i)

    # Leaves
    all_leaves = EcplCalander.objects.filter(Q(rm1=emp_name), Q(date=today), Q(applied_status=True),
                                              Q(att_approved='approved'), Q(att_applied='PL') |
                                              Q(att_applied='Hald Day') | Q(att_applied='Sick Leave') | Q(att_applied='Maternity Leave')).order_by('emp_name')

    leaves_today = EcplCalander.objects.filter(Q(rm1=emp_name), Q(date=today), Q(applied_status=True),
                                             Q(att_approved='approved'), Q(att_applied='PL') |
                                             Q(att_applied='Hald Day') | Q(att_applied='Sick Leave') | Q(
            att_applied='Maternity Leave')).count()
    #counts
    emp_count = Employee.objects.filter(emp_rm1=emp_name).count()
    active_today = EcplCalander.objects.filter(Q(rm1=emp_name) ,Q(date=today),Q(applied_status=True),Q(att_approved='approved'),Q(att_applied='present') |
                               Q(att_applied='HD')).count()
    unmarked_today = emp_count-active_today

    data = {'emp_name': emp_name, 'emp': emp,'cal':cal, 'att_details':att_details,
            'emp_count':emp_count,'active_today':active_today,'unmarked_today':unmarked_today,
            'all_active':all_active,'all_present':all_present,'unmarked_emps':unmarked_emps,
            'all_leaves':all_leaves,'leaves_today':leaves_today
            }
    return render(request, 'ams/rm-dashboard.html', data)



def indexPage(request):
    team_name = 'Gubagoo'
    emp_team_obj = Employee.objects.filter(emp_process = team_name)
    data = {'team':emp_team_obj}
    return render(request,'ams/index.html',data)

def employeeDetails(request,pk):
    emp_id = pk
    emp_obj = Employee.objects.get(emp_id = emp_id)
    data = {'employee':emp_obj}
    return render(request, 'ams/employee-details.html', data)


def applyAttendace(request):
    if request.method == 'POST':
        date = request.POST['date']
        att_applied = request.POST['att_applied']
        rm1 = request.POST['rm1']
        rm2 = request.POST['rm2']
        rm3 = request.POST['rm3']
        emp_id = request.user.profile.emp_id
        emp_name = request.user.profile.emp_name
        team = request.user.profile.emp_process
        now = datetime.now()
        cal = EcplCalander.objects.create(
            team = team, date = date, emp_name = emp_name, emp_id = emp_id,
            att_applied = att_applied,applied_by = emp_id,applied_status = True,
            rm1 = rm1, rm2 = rm2, rm3 = rm3,
            applied_on = now
        )
        cal.save()

        return redirect('/ams/agent-dashboard')
    else:
        pass

def rmApproval(request,id):
    if request.method == 'POST':
        usr = request.user.profile.emp_name
        id =id
        now = datetime.now()
        att_approved = request.POST['att_approved']
        cal = EcplCalander.objects.get(id=id)
        cal.att_approved = att_approved
        cal.approved_status = True
        cal.approved_on=now
        cal.appoved_by = usr

        cal.save()

        return redirect('/ams/tl-dashboard')

