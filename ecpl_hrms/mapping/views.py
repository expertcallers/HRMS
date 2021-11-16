from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import *
from django.db.models import Avg, Max, Min, Sum

from itertools import chain

# Create your views here.
@login_required
def employeeMapping(request):
    if request.method == 'POST':

        emp_name = request.POST['emp_name']
        employees = Employee.objects.filter(emp_name__icontains=emp_name)
        if employees:
            messages.info(request,'Search Result')
        else:
            messages.info(request,'The requested employee not found')

        ## Largest Employee ID
        emp = Employee.objects.all().order_by('-emp_id')[:1]

        teams = Employee.objects.values_list('emp_process',flat=True).distinct()
        data = {'employees': employees,'teams':teams,'emp_name':emp_name,'emp':emp}
        return render(request, 'mapping/index.html', data)
    else:

        ## Largest Employee ID
        emp = Employee.objects.all().order_by('-emp_id')[:1]

        employees = Employee.objects.all()
        teams = Employee.objects.values_list('emp_process', flat=True).distinct()
        data = {'employees':employees,'teams':teams,'emp':emp}
        return render(request,'mapping/index.html',data)

def mappingLogin(request):

    if request.method == 'POST':

        form = AuthenticationForm(data=request.POST)  # Login form
        if form.is_valid():
            # login the user
            user = form.get_user()
            login(request, user)
            if request.user.profile.pc == False:
                return redirect('/mapping/change-password')

            return redirect('/mapping/home')
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
            return redirect('/mapping/login')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request,'mapping/change-password.html', {'form': form})


@login_required
def teamWiseData(request):
    if request.method == 'POST':
        team = request.POST['team']
        employees = Employee.objects.filter(emp_process=team)
        messages.info(request, 'Search Result')
        teams = Employee.objects.values_list('emp_process',flat=True).distinct()
        data = {'employees': employees,'teams':teams}
        return render(request, 'mapping/index.html', data)
    else:
        employees = Employee.objects.all()
        data = {'employees':employees}
        return render(request,'mapping/index.html',data)

def empIDwiseData(request):

    if request.method == 'POST':
        emp_id = request.POST['emp_id']
        employees = Employee.objects.filter(emp_id=emp_id)
        if employees:
            messages.info(request,'Search Result')
        else:
            messages.info(request,'The requested employee not found')

        teams = Employee.objects.values_list('emp_process',flat=True).distinct()
        data = {'employees': employees,'teams':teams,'emp_id':emp_id}
        return render(request, 'mapping/index.html', data)
    else:

        employees = Employee.objects.all()
        teams = Employee.objects.values_list('emp_process', flat=True).distinct()
        data = {'employees': employees, 'teams': teams}
        return render(request, 'mapping/index.html', data)


@login_required
def updateEmployeeProfile(request):
    if request.method == 'POST':
        emp_id = request.POST['emp_id']
        emp = Employee.objects.get(emp_id = emp_id)
        teams = Employee.objects.values_list('emp_process', flat=True).distinct()
        desis = Employee.objects.values_list('emp_desi', flat=True).distinct()
        rm1s = Employee.objects.values_list('emp_rm1',flat=True).distinct()
        rm2s = Employee.objects.values_list('emp_rm2',flat=True).distinct()
        rm3s = Employee.objects.values_list('emp_rm3',flat=True).distinct()
        data = {'emp':emp,'teams':teams,'desis':desis,'rm1s':rm1s,'rm2s':rm2s,'rm3s':rm3s}
        return render(request,'mapping/update-to-database.html',data)
    else:
        employees = Employee.objects.all().order_by('emp_name')
        teams = Employee.objects.values_list('emp_process', flat=True).distinct()
        data = {'employees':employees,'teams':teams}
        return render(request,'mapping/update-employee-profile.html',data)

@login_required
def updateToSystem(request):
    if request.method == 'POST':
        userr = request.user.profile.emp_name
        emp_name = request.POST['emp_name']
        emp_id = request.POST['emp_id']
        emp_desi = request.POST['emp_desi']
        emp_process = request.POST['emp_process']
        emp_rm1 = request.POST['emp_rm1']
        emp_rm2 = request.POST['emp_rm2']
        emp_rm3 = request.POST['emp_rm3']
        history = emp_rm1 +"/" + emp_rm2+"/" + emp_rm3

        id = request.POST['id']
        pfl = Profile.objects.get(emp_id = emp_id)
        pfl.emp_name = emp_name
        pfl.emp_id = emp_id
        pfl.emp_desi = emp_desi
        pfl.emp_process = emp_process
        pfl.emp_rm1 = emp_rm1
        pfl.emp_rm2 = emp_rm2
        pfl.emp_rm3 = emp_rm3
        pfl.save()

        emp = Employee.objects.get(id=id)
        emp.emp_name = emp_name
        emp.emp_id = emp_id
        emp.emp_desi = emp_desi
        emp.emp_process = emp_process
        emp.emp_rm1 = emp_rm1
        emp.emp_rm2 = emp_rm2
        emp.emp_rm3 = emp_rm3
        emp.save()
        mh = MappingHistory.objects.create(
            updated_by = userr,emp_name = emp_name, emp_id=emp_id, rm1=emp_rm1, rm2=emp_rm2, rm3=emp_rm3, team = emp_process,
            history=history,
            )
        mh.save()
        messages.info(request,'Employee Profile updated successfully !')
        return redirect('/mapping/home')
    else:
        return redirect('/mapping/login')


# Update Team's RMS

def updateTeamRms(request):
    if request.method == 'POST':
        team = request.POST['team']
        rm1s = Employee.objects.filter(emp_process=team).values_list('emp_rm1',flat=True).distinct().order_by(
            'emp_rm1')
        rm2s = Employee.objects.filter(emp_process=team).values_list('emp_rm2', flat=True).distinct().order_by(
            'emp_rm2')
        rm3s = Employee.objects.filter(emp_process=team).values_list('emp_rm3', flat=True).distinct().order_by(
            'emp_rm3')
        data = {'rm1s':rm1s,'rm2s':rm2s,'rm3s':rm3s,'team':team}
        return render(request,'mapping/update-team-rms.html',data)

    else:
        pass


def updateRM1forTeam(request,rm1,team):
    rms = Employee.objects.exclude(emp_desi='Client Relationship Officer')
    data = {'team':team,'rm1':rm1,'rms':rms}
    return render(request,'mapping/rm1-team-details.html',data)

def updateTeamRm1(request):
    if request.method == 'POST':
        userr = request.user.profile.emp_name
        team = request.POST['team']
        rm1 = request.POST['rm1']
        new_rm1 = request.POST['new_rm1']

        rm = Employee.objects.filter(emp_process = team, emp_rm1 = rm1)
        for i in rm:
            i.emp_rm1 = new_rm1
            i.save()

        pfl = Profile.objects.filter(emp_process = team, emp_rm1 = rm1)
        for j in pfl:
            j.emp_rm1 = new_rm1
            j.save()

        mh = MappingHistoryTeam.objects.create(updated_by = userr,team = team,category = "RM 1", new_value = new_rm1)
        mh.save()
        messages.info(request, 'Team RM1 updated successfully !')
        return redirect('/mapping/home')

# rm2
def updateRM2forTeam(request,rm2,team):
    rms = Employee.objects.exclude(emp_desi='Client Relationship Officer')
    data = {'team':team,'rm2':rm2,'rms':rms}
    return render(request,'mapping/rm2-team-details.html',data)

def updateTeamRm2(request):
    if request.method == 'POST':
        userr = request.user.profile.emp_name
        team = request.POST['team']
        rm2 = request.POST['rm2']
        new_rm2 = request.POST['new_rm2']

        rm = Employee.objects.filter(emp_process = team, emp_rm2 = rm2)
        for i in rm:
            i.emp_rm2 = new_rm2
            i.save()

        pfl = Profile.objects.filter(emp_process=team, emp_rm2 = rm2)
        for j in pfl:
            j.emp_rm2 = new_rm2
            j.save()

        mh = MappingHistoryTeam.objects.create(updated_by=userr, team=team, category="RM 2", new_value=new_rm2)
        mh.save()
        messages.info(request, 'Team RM2 updated successfully !')
        return redirect('/mapping/home')

# rm3
def updateRM3forTeam(request,rm3,team):
    rms = Employee.objects.exclude(emp_desi='Client Relationship Officer')
    data = {'team':team,'rm3':rm3,'rms':rms}
    return render(request,'mapping/rm3-team-details.html',data)

def updateTeamRm3(request):
    if request.method == 'POST':
        userr = request.user.profile.emp_name
        team = request.POST['team']
        rm3 = request.POST['rm3']
        new_rm3 = request.POST['new_rm3']

        rm = Employee.objects.filter(emp_process = team, emp_rm3 = rm3)
        for i in rm:
            i.emp_rm3 = new_rm3
            i.save()

        pfl = Profile.objects.filter(emp_process=team, emp_rm3 = rm3)
        for j in pfl:
            j.emp_rm3 = new_rm3
            j.save()

        mh = MappingHistoryTeam.objects.create(updated_by=userr, team=team, category="RM 3", new_value=new_rm3)
        mh.save()
        messages.info(request, 'Team RM3 updated successfully !')
        return redirect('/mapping/home')


def createUserandProfile(request):

    emp = Employee.objects.all()
    for i in emp:
        user = User.objects.filter(username=i.emp_id)
        if user.exists():
            prof = Profile.objects.filter(emp_id = i.emp_id)
            if prof.exists():
                pass
            else:
                profile = Profile.objects.create(
                    emp_id=i.emp_id, emp_name=i.emp_name, emp_desi=i.emp_desi,
                    emp_rm1=i.emp_rm1, emp_rm2=i.emp_rm2, emp_rm3=i.emp_rm3,
                    emp_process=i.emp_process, user_id=i.emp_id
                )
                profile.save()

        else:
            user = User.objects.create_user(id=i.id, username=i.emp_id, password=str(i.emp_id))

            profile = Profile.objects.create(
                emp_id = i.emp_id,emp_name = i.emp_name, emp_desi = i.emp_desi,
                emp_rm1 = i.emp_rm1, emp_rm2 = i.emp_rm2, emp_rm3 = i.emp_rm3,
                emp_process = i.emp_process, user_id = i.id
                                          )
            profile.save()
            user.save()





def correct_process(request):

    e = Employee.objects.all()
    for i in e:

        process = str(i.emp_process)
        i.emp_process = process
        i.save()
#        print(i.emp_process)


def exportMapping(request):
    import xlwt

    if request.method == 'POST':
        team = request.POST['team']
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

        if team =='all':
            rows = Employee.objects.all().values_list(
            'emp_id', 'emp_name', 'emp_desi', 'emp_rm1', 'emp_rm2', 'emp_rm3', 'emp_process'
            )
        else:
            rows = Employee.objects.filter(emp_process = team).values_list(
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

def nameChanger(request):
    emp_new_rm1 = 'Harish Kumar S'
    emp = Employee.objects.filter(emp_rm1='Harish Kumar',emp_process='Gubagoo')
    for i in emp:
        i.emp_rm1 = emp_new_rm1
        i.save()



def searchForEmployee(request):
    emp_id = request.POST['emp_id']
    try:
        emp = Employee.objects.get(emp_id=emp_id)
        messages.info(request, 'Employee Found, Please select Below !')
    except Employee.DoesNotExist:
        messages.info(request,'Not Found, Please search below !')
        emp=None
    employees = Employee.objects.all().order_by('emp_name')
    teams = Employee.objects.values_list('emp_process', flat=True).distinct()
    data = {'emp':emp,'employees':employees,'teams':teams}
    return render(request,'mapping/update-employee-profile.html',data)