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
        data = {'employees':employees}
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
        data = {'employees':employees}
        return render(request,'mapping/update-employee-profile.html',data)
@login_required
def updateToSystem(request):
    if request.method == 'POST':
        emp_name = request.POST['emp_name']
        emp_id = request.POST['emp_id']
        emp_desi = request.POST['emp_desi']
        emp_process = request.POST['emp_process']
        id = request.POST['id']
        emp = Employee.objects.get(id=id)
        emp.emp_name = emp_name
        emp.emp_id = emp_id
        emp.emp_desi = emp_desi
        emp.emp_process = emp_process
        emp.save()
        return redirect('/mapping/home')
    else:
        return redirect('/mapping/login')


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


