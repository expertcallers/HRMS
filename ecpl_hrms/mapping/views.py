from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from .models import *
from itertools import chain

# Create your views here.
@login_required
def employeeMapping(request):
    if request.method == 'POST':
        emp_name = request.POST['emp_name']
        employees = Employee.objects.filter(emp_name__icontains=emp_name)
        teams = Employee.objects.values_list('emp_process',flat=True).distinct()
        data = {'employees': employees,'teams':teams}
        return render(request, 'mapping/index.html', data)
    else:
        employees = Employee.objects.all()
        teams = Employee.objects.values_list('emp_process', flat=True).distinct()
        data = {'employees':employees,'teams':teams}
        return render(request,'mapping/index.html',data)

def mappingLogin(request):

    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)  # Login form
        if form.is_valid():
            # login the user
            user = form.get_user()
            login(request, user)
            return redirect('/mapping/home')
        else:
            form = AuthenticationForm()
            m='Invalid Credentials !'
            return render(request,'mapping/login.html',{'form':form,'m':m})
    else:
        logout(request)
        form = AuthenticationForm()
        return render(request, 'mapping/login.html', {'form': form})
@login_required
def teamWiseData(request):
    if request.method == 'POST':
        team = request.POST['team']
        employees = Employee.objects.filter(emp_process=team)
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
        teams = Employee.objects.values_list('emp_process',flat=True).distinct()
        data = {'employees': employees,'teams':teams}
        return render(request, 'mapping/index.html', data)
    else:
        pass


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
        emp_name = request.POST['emp_name']
        emp_id = request.POST['emp_id']
        emp_desi = request.POST['emp_desi']
        emp_process = request.POST['emp_process']
        emp_rm1 = request.POST['emp_rm1']
        emp_rm2 = request.POST['emp_rm2']
        emp_rm3 = request.POST['emp_rm3']
        id = request.POST['id']
        emp = Employee.objects.get(id=id)
        emp.emp_name = emp_name
        emp.emp_id = emp_id
        emp.emp_desi = emp_desi
        emp.emp_process = emp_process
        emp.emp_rm1 = emp_rm1
        emp.emp_rm2 = emp_rm2
        emp.emp_rm3 = emp_rm3
        emp.save()
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
        team = request.POST['team']
        rm1 = request.POST['rm1']
        new_rm1 = request.POST['new_rm1']

        rm = Employee.objects.filter(emp_process = team, emp_rm1 = rm1)
        for i in rm:
            i.emp_rm1 = new_rm1
            i.save()
        return redirect('/mapping/update-employee-profile')

# rm2
def updateRM2forTeam(request,rm2,team):
    rms = Employee.objects.exclude(emp_desi='Client Relationship Officer')
    data = {'team':team,'rm2':rm2,'rms':rms}
    return render(request,'mapping/rm2-team-details.html',data)

def updateTeamRm2(request):
    if request.method == 'POST':
        team = request.POST['team']
        rm2 = request.POST['rm2']
        new_rm2 = request.POST['new_rm2']

        rm = Employee.objects.filter(emp_process = team, emp_rm2 = rm2)
        for i in rm:
            i.emp_rm2 = new_rm2
            i.save()
        return redirect('/mapping/update-employee-profile')

# rm3
def updateRM3forTeam(request,rm3,team):
    rms = Employee.objects.exclude(emp_desi='Client Relationship Officer')
    data = {'team':team,'rm3':rm3,'rms':rms}
    return render(request,'mapping/rm3-team-details.html',data)

def updateTeamRm3(request):
    if request.method == 'POST':
        team = request.POST['team']
        rm3 = request.POST['rm3']
        new_rm3 = request.POST['new_rm3']

        rm = Employee.objects.filter(emp_process = team, emp_rm3 = rm3)
        for i in rm:
            i.emp_rm3 = new_rm3
            i.save()
        return redirect('/mapping/update-employee-profile')



def createUserandProfile(request):
    emp = Employee.objects.all()
    for i in emp:
        user = User.objects.filter(username=i.emp_id)
        if user.exists():
            print(i.emp_name + ' ' + 'exist')
        else:
            user = User.objects.create_user(id=i.emp_id, username=i.emp_id, password=str(i.emp_id))

            profile = Profile.objects.create(
                emp_id = i.emp_id,emp_name = i.emp_name, emp_desi = i.emp_desi,
                emp_rm1 = i.emp_rm1, emp_rm2 = i.emp_rm2, emp_rm3 = i.emp_rm3,
                emp_process = i.emp_process, user_id = i.emp_id
                                          )
            profile.save()
            user.save()
            print('created'+ i.emp_name)


