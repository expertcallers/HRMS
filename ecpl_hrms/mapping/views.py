from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import *
from django.apps import apps
Campaigns = apps.get_model('ams', 'Campaigns')
from django.db.models import Avg, Max, Min, Sum, Q
from itertools import chain
import xlwt

# Manager List
manager_list = ['Team Leader','Assistant Manager','Subject Matter Expert', 'Trainer','Learning and Development Head',
              'Process Trainer','Sales Trainer',
              'Quality Head','Operations Manager','Service Delivery Manager','Command Centre Head',
              'HR','HR Manager','Manager ER','HR Lead','Sr Recruiter','MIS Executive HR',
              'Lead HRBP','Employee Relations Specialist','Payroll Specialist','Recruiter','HR Generalist',
              'Associate Director','Chief Executive Officer','Chief Compliance Officer','Chief Technology Officer',
              'Managing Director','Vice President','Board member',
              'IT Manager',
              ]

# Mapping Home Page
@login_required
def employeeMapping(request): 
    if request.user.profile.emp_desi in manager_list:
        if request.method == 'POST':
            emp_name = request.POST['emp_name']
            employees = Profile.objects.filter(agent_status = 'Active',emp_name__icontains=emp_name)
            if employees:
                messages.info(request,'Search Result')
            else:
                messages.info(request,'The requested employee not found')
            teams = Campaigns.objects.all().order_by('name')
            data = {'employees': employees,'teams':teams,'emp_name':emp_name,}
            return render(request, 'mapping/index.html', data)
        else:
            employees = Profile.objects.all()
            teams = Campaigns.objects.all().order_by('name')
            data = {'employees':employees,'teams':teams,}
            return render(request,'mapping/index.html',data)
    else:
        logout(request)
        form = AuthenticationForm()
        m='Not Authorised to view this page !'
        return render(request,'mapping/login.html',{'form':form,'m':m})

# Login Page 
def mappingLogin(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)  # Login form
        if form.is_valid():
            # login the user
            user = form.get_user()
            login(request, user)
            if request.user.profile.emp_desi in manager_list:
                if request.user.profile.pc == False:
                    return redirect('/mapping/change-password')
                return redirect('/mapping/home')
            else:
                form = AuthenticationForm()
                m='Not Authorised to view this page !'
                return render(request,'mapping/login.html',{'form':form,'m':m})
        else:
            form = AuthenticationForm()
            m='Invalid Credentials !'
            return render(request,'mapping/login.html',{'form':form,'m':m})
    else:
        logout(request)
        form = AuthenticationForm()
        return render(request, 'mapping/login.html', {'form': form})

def mappingLogout(request):
    logout(request)
    return redirect('/mapping/login')

@login_required
def change_password(request): # Corrected
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
            return redirect('/mapping/login')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request,'mapping/change-password.html', {'form': form})


@login_required # Corrected
def teamWiseData(request):
    if request.method == 'POST':
        team_id = request.POST['team_id']
    
        employees = Profile.objects.filter(emp_process_id=team_id,agent_status = 'Active')
        messages.info(request, 'Search Result')
        teams = Campaigns.objects.all().order_by('name')
        data = {'employees': employees,'teams':teams}
        return render(request, 'mapping/index.html', data)
    else:
        employees = Profile.objects.all()
        data = {'employees':employees}
        return render(request,'mapping/index.html',data)

@login_required # Corrected
def empIDwiseData(request):
    if request.method == 'POST':        
        emp_id = request.POST['emp_id']
        employees = Profile.objects.filter(emp_id=emp_id,agent_status = 'Active')
        if employees:
            messages.info(request,'Search Result')
        else:
            messages.info(request,'The requested employee not found')
        teams = Campaigns.objects.all()
        data = {'employees': employees,'teams':teams,'emp_id':emp_id}
        return render(request, 'mapping/index.html', data)
    else:
        employees = Profile.objects.all()
        teams = Campaigns.objects.all()
        data = {'employees': employees, 'teams': teams}
        return render(request, 'mapping/index.html', data)

@login_required # Corrected
def updateEmployeeProfile(request):
    if request.method == 'POST':
        emp_id = request.POST['emp_id']
        emp = Profile.objects.get(emp_id = emp_id)
        teams = Campaigns.objects.all()
        desis = Profile.objects.values_list('emp_desi', flat=True).distinct()
        rms = Profile.objects.filter(emp_desi__in = manager_list,agent_status = 'Active').order_by('emp_name')
        data = {'emp':emp,'teams':teams,'desis':desis,'rms':rms}
        return render(request,'mapping/update-to-database.html',data)
    else:
        employees = Profile.objects.all().order_by('emp_name')
        teams = Campaigns.objects.all()
        data = {'employees':employees,'teams':teams}
        return render(request,'mapping/update-employee-profile.html',data)

@login_required
def updateToSystem(request):
    if request.method == 'POST':
        userr = request.user.profile.emp_name
        emp_name = request.POST['emp_name']
        emp_id = request.POST['emp_id']
        emp_desi = request.POST['emp_desi']
        emp_process_id = request.POST['emp_process_id']
        emp_rm1_id = request.POST['emp_rm1_id']
        emp_rm2_id = request.POST['emp_rm2_id']
        emp_rm3_id = request.POST['emp_rm3_id']        
        pfl = Profile.objects.get(emp_id = emp_id)
        old_rm1 = Profile.objects.get(emp_id = emp_id).emp_rm1
        old_rm2 = Profile.objects.get(emp_id = emp_id).emp_rm2
        old_rm3 = Profile.objects.get(emp_id = emp_id).emp_rm3
        old_process = Profile.objects.get(emp_id = emp_id).emp_process

        history = old_rm1 +"/" + old_rm2 +"/" + old_rm3 + "/"+ old_process
        
        rm1 = Profile.objects.get(emp_id = emp_rm1_id).emp_name
        rm2 = Profile.objects.get(emp_id = emp_rm2_id).emp_name
        rm3 = Profile.objects.get(emp_id = emp_rm3_id).emp_name
        process = Campaigns.objects.get(id=emp_process_id).name
        pfl.emp_name = emp_name
        pfl.emp_id = emp_id
        pfl.emp_desi = emp_desi
        pfl.emp_process_id = emp_process_id
        pfl.emp_process = process
        pfl.emp_rm1_id = emp_rm1_id
        pfl.emp_rm2_id = emp_rm2_id
        pfl.emp_rm3_id = emp_rm3_id
        pfl.emp_rm1 = rm1
        pfl.emp_rm2 = rm2
        pfl.emp_rm3 = rm3
        pfl.save()
        mh = MappingHistory.objects.create(
            updated_by = userr,emp_name = emp_name, emp_id=emp_id, rm1=rm1, rm2=rm2, rm3=rm3, team = process,
            history=history)
        mh.save()
        messages.info(request,'Employee Profile updated successfully !')
        return redirect('/mapping/home')
    else:
        return redirect('/mapping/login')


def createUserandProfile(request): # Need to work
    emp = Data.objects.all()
    for i in emp:
        user = User.objects.filter(username=i.emp_id)
        if user.exists():
            usr = User.objects.get(username=i.emp_id)
            prof = Profile.objects.filter(emp_id = i.emp_id)
            if prof.exists():
                pass
            else:
                profile = Profile.objects.create(
                    emp_id=i.emp_id, emp_name=i.emp_name, emp_desi=i.emp_desi,
                    emp_rm1=i.emp_rm1, emp_rm2=i.emp_rm2, emp_rm3=i.emp_rm3,
                    emp_process=i.emp_process, user=usr, 
                    emp_rm1_id = i.emp_rm1_id,
                    emp_rm2_id = i.emp_rm2_id,
                    emp_rm3_id = i.emp_rm3_id,
                    emp_process_id = int(i.emp_process_id),
                )
                profile.save()              

        else:
            user = User.objects.create_user(username=i.emp_id, password=str(i.emp_id))
            user.save()
            usr = User.objects.get(username=i.emp_id)
            profile = Profile.objects.create(
                emp_id = i.emp_id,emp_name = i.emp_name, emp_desi = i.emp_desi,
                emp_rm1 = i.emp_rm1, emp_rm2 = i.emp_rm2, emp_rm3 = i.emp_rm3,
                emp_process = i.emp_process, user = usr,
                 emp_rm1_id = i.emp_rm1_id,
                    emp_rm2_id = i.emp_rm2_id,
                    emp_rm3_id = i.emp_rm3_id,
                    emp_process_id = i.emp_process_id,
                                          )
            profile.save()

@login_required
def exportMapping(request):
    if request.method == 'POST':
        team_id = request.POST['team_id']
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="mapping.xls"'
        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Users Data')  # this will make a sheet named Users Data
        # Sheet header, first row
        row_num = 0
        font_style = xlwt.XFStyle()
        font_style.font.bold = True
        columns = [
                    'Emp ID','Emp Name','Designation','RM 1','RM 2','RM 3','Team'
                  ]
        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], font_style)  # at 0 row 0 column
        # Sheet body, remaining rows
        font_style = xlwt.XFStyle()
        if team_id =='all':
            rows = Profile.objects.all().values_list(
            'emp_id', 'emp_name', 'emp_desi', 'emp_rm1', 'emp_rm2', 'emp_rm3', 'emp_process'
            )
        else:
            rows = Profile.objects.filter(emp_process_id = team_id).values_list(
                'emp_id', 'emp_name', 'emp_desi', 'emp_rm1', 'emp_rm2', 'emp_rm3', 'emp_process'
                )
        import datetime
        rows = [[x.strftime("%Y-%m-%d %H:%M") if isinstance(x, datetime.datetime) else x for x in row] for row in
                rows]
        for row in rows:
            row_num += 1
            for col_num in range(len(row)):
                ws.write(row_num, col_num, row[col_num], font_style)
        wb.save(response)
        return response

@login_required # Corrected
def searchForEmployee(request):
    if request.method == 'POST':
        emp_id = request.POST['emp_id']
        try:
            emp = Profile.objects.get(emp_id=emp_id)
            messages.info(request, 'Employee Found, Please select Below !')
        except Profile.DoesNotExist:
            messages.info(request,'Not Found, Please search below !')
            emp=None
        employees = Profile.objects.all().order_by('emp_name')
        teams = Campaigns.objects.all()
        data = {'emp':emp,'employees':employees,'teams':teams}
        return render(request,'mapping/update-employee-profile.html',data)
    else:
        emp=None
        employees = Profile.objects.all().order_by('emp_name')
        teams = Campaigns.objects.all()
        data = {'emp':emp,'employees':employees,'teams':teams}
        return render(request,'mapping/update-employee-profile.html',data)

    