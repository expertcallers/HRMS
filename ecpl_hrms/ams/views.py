from datetime import datetime
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import *
from calendar import Calendar, monthrange
from django.contrib import messages
from datetime import date, timedelta
import calendar
from django.apps import apps
Employee = apps.get_model('mapping', 'Employee')
Profile = apps.get_model('mapping','Profile')

c = Calendar()
from datetime import date
from django.db.models import Q

manager_list = ['Associate Director','Assistant Manager','Team Leader','Operations Manager','Trainer','Command Centre Head','Process Trainer','Learning and Development Head','Service Delivery Manager','Trainer Sales',
                        'Team Leader - GB','Head-CC']

hr_list = ['HR']

# Create your views here.
def loginPage(request):
    logout(request)
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

            if request.user.profile.emp_desi in manager_list:
                return redirect('/ams/tl-dashboard')
            elif request.user.profile.emp_desi in hr_list:
                return redirect('/ams/hr-dashboard')
            else:
                return redirect('/ams/agent-dashboard')
        else:
            form = AuthenticationForm()
            messages.info(request,'Invalid Credentials')
            teams = Employee.objects.values_list('emp_process', flat=True).distinct()
            data = {'teams': teams, 'form': form}
            return render(request, 'ams/login.html', data)
    else:
        logout(request)
        form = AuthenticationForm()
        teams = Employee.objects.values_list('emp_process', flat=True).distinct()
        data = {'teams': teams, 'form': form}
        return render(request, 'ams/login.html', data)

def redirectTOAllDashBoards(request,id):

    if request.user.profile.emp_desi in manager_list:
        return redirect('/ams/tl-dashboard')
    elif request.user.profile.emp_desi in hr_list:
        return redirect('/ams/hr-dashboard')
    else:
        return redirect('/ams/agent-dashboard')

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

@login_required
def agentDashBoard(request):
    today = date.today()
    yesterday = today - timedelta(days=1)
    dby_date = yesterday - timedelta(days=1)

    emp_name = request.user.profile.emp_name
    emp_id = request.user.profile.emp_id
    emp = Employee.objects.get(emp_id = emp_id)
    try:
        cal_day = EcplCalander.objects.get(date=today,applied_status=True,emp_id=emp_id)
        tdy_date = today
        today = 'Applied'
    except EcplCalander.DoesNotExist:
        today = str(today)
        tdy_date = today

    try:
        cal_yday = EcplCalander.objects.get(date=yesterday, applied_status=True, emp_id=emp_id)
        yst_date = yesterday
        yesterday = 'Applied'

    except EcplCalander.DoesNotExist:
        yst_date = yesterday
        yesterday = str(yesterday)

    try:
        dby = EcplCalander.objects.get(date=dby_date, applied_status=True, emp_id=emp_id)
        dby_date = dby_date
        day_befor_yest = 'Applied'
    except EcplCalander.DoesNotExist:
        dby_date = dby_date
        day_befor_yest = str(dby_date)

    #attendance status
    cal = EcplCalander.objects.filter(emp_id=emp_id).order_by('-date')[:3]

    # Month view
    ########### Month View ############
    month_days = []
    todays_date = date.today()
    year = todays_date.year
    month = todays_date.month
    a, num_days = calendar.monthrange(year, month)
    start_date = date(year, month, 1)
    end_date = date(year, month, num_days)
    delta = timedelta(days=1)
    while start_date <= end_date:
        month_days.append(start_date.strftime("%Y-%m-%d"))
        start_date += delta

    month_cal = []
    for i in month_days:

        dict = {}
        try:
            st = EcplCalander.objects.get(Q(date=i),Q(emp_name = emp_name)).att_actual

        except EcplCalander.DoesNotExist:
            st = 'Unmarked'
        dict['dt'] = i
        dict['st'] = st
        month_cal.append(dict)


    data = {'emp_name':emp_name,'emp':emp,'date':today,'yesterday':yesterday,'cal':cal,'month_cal':month_cal,
            'yst_date':yst_date,'tdy_date':tdy_date,
            'dby_date':dby_date,'day_befor_yest':day_befor_yest}

    return render(request,'ams/agent-dashboard-new.html',data)

def tlDashboard(request):
    emp_name = request.user.profile.emp_name
    emp_id = request.user.profile.emp_id
    emp = Employee.objects.get(emp_id=emp_id)
    cal = EcplCalander.objects.filter(approved_status=False,rm1=emp_name)
    total_req = cal.count()
    # details
    today = date.today()
    today = str(today)
    att_details = EcplCalander.objects.filter(date = today,rm1=emp_name)
    all_active = Employee.objects.filter(emp_rm1=emp_name).order_by('emp_name')
    all_present = EcplCalander.objects.filter(Q(rm1=emp_name) ,Q(date=today),Q(applied_status=True),Q(att_approved='approved'),Q(att_applied='present') |
                               Q(att_applied='Half Day')).order_by('emp_name')

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
                               Q(att_applied='Half Day')).count()
    unmarked_today = emp_count-active_today

    ################

    present_count = EcplCalander.objects.filter(Q(rm1=emp_name),Q(date=today),Q(att_actual='present')).count()
    absent_count = EcplCalander.objects.filter(Q(rm1=emp_name), Q(date=today), Q(att_actual='Absent')).count()
    week_off_count = EcplCalander.objects.filter(Q(rm1=emp_name), Q(date=today), Q(att_actual='Week OFF')).count()
    comp_off_count = EcplCalander.objects.filter(Q(rm1=emp_name), Q(date=today), Q(att_actual='Comp OFF')).count()
    half_day_count = EcplCalander.objects.filter(Q(rm1=emp_name), Q(date=today), Q(att_actual='Half Day')).count()

    holiday_count = EcplCalander.objects.filter(Q(rm1=emp_name), Q(date=today), Q(att_actual='Holiday')).count()
    unmarked_count = emp_count - (present_count + absent_count + week_off_count + comp_off_count + half_day_count + holiday_count)

    # Mapping Tickets >>

    map_tickets_counts = MappingTickets.objects.filter(new_rm3 = emp_name,status=False).count()

    data = {'emp_name': emp_name, 'emp': emp,'cal':cal, 'att_details':att_details,
            'emp_count':emp_count,'active_today':active_today,'unmarked_today':unmarked_today,
            'all_active':all_active,'all_present':all_present,'unmarked_emps':unmarked_emps,
            'all_leaves':all_leaves,'leaves_today':leaves_today,'total_req':total_req,

            'present_count':present_count,'absent_count':absent_count,'week_off_count':week_off_count,
            'comp_off_count':comp_off_count,'half_day_count':half_day_count,'holiday_count':holiday_count,
            'unmarked_count':unmarked_count,

            'map_tickets_counts':map_tickets_counts
            }
    return render(request, 'ams/rm-dashboard-new.html', data)

def hrDashboard(request):
    emp_id = request.user.profile.emp_id
    emp = Employee.objects.get(emp_id=emp_id)
    data = {'emp':emp}
    return render(request,'ams/hr_dashboard.html',data)

def onboardingHR(request):
    if request.method == 'POST':

        usr_name = request.user.profile.emp_name

        emp_name = request.POST["emp_name"]
        emp_dob = request.POST["emp_dob"]
        emp_desi = request.POST["emp_desg"]
        emp_process = request.POST["emp_pro"]
        emp_pan = request.POST["emp_pan"]
        emp_aadhar = request.POST["emp_aad"]
        emp_father_name = request.POST["emp_fat"]
        emp_marital_status = request.POST["emp_mar"]
        emp_email = request.POST["emp_email"]
        emp_phone = request.POST["emp_ph"]
        emp_alt_phone = request.POST["emp_alph"]
        emp_present_address = request.POST["emp_add"]
        emp_permanent_address = request.POST["emp_pre_add"]
        emp_blood_group = request.POST["emp_blo"]
        emp_emergency_person = request.POST["emp_emer_name"]
        emp_emergency_number = request.POST["emp_emer_ph"]
        emp_emergency_address = request.POST["emp_emer_add"]
        emp_edu_quali = request.POST["emp_high_qua"]
        emp_edu_course = request.POST["emp_cou"]
        emp_edu_institute = request.POST["emp_ins"]
        emp_pre_exp = request.POST["emp_exp"]
        emp_pre_industry = request.POST["emp_ind"]
        emp_pre_org_name = request.POST["emp_pre_org"]
        emp_pre_desi = request.POST["emp_pre_desg"]
        emp_prev_tenure = request.POST["emp_pre_empl"]
        emp_bank_name = request.POST["emp_bank_name"]
        emp_account_no = request.POST["emp_bank_no"]
        emp_bank_ifsc = request.POST["emp_bank_ifsc"]
        emp_aadhar = request.FILES["emp_up_aad"]
        emp_pan = request.FILES["emp_up_pan"]
        emp_idcard = request.FILES["emp_up_id"]
        emp_certificate = request.FILES["emp_up_edu"]
        emp_exp_letter = request.FILES["emp_up_cer"]
        emp_passbook = request.FILES["emp_up_bank"]

        e = Onboarding()
        e.emp_name = emp_name
        e.emp_dob = emp_dob
        e.emp_desi = emp_desi
        e.emp_process = emp_process
        e.emp_pan = emp_pan
        e.emp_aadhar = emp_aadhar
        e.emp_father_name = emp_father_name
        e.emp_marital_status = emp_marital_status
        e.emp_email = emp_email
        e.emp_phone = emp_phone
        e.emp_alt_phone = emp_alt_phone
        e.emp_present_address = emp_present_address
        e.emp_permanent_address = emp_permanent_address
        e.emp_blood_group = emp_blood_group
        e.emp_emergency_person = emp_emergency_person
        e.emp_emergency_number = emp_emergency_number
        e.emp_emergency_address = emp_emergency_address
        e.emp_edu_quali = emp_edu_quali
        e.emp_edu_course = emp_edu_course
        e.emp_edu_institute = emp_edu_institute
        e.emp_pre_exp = emp_pre_exp
        e.emp_pre_industry = emp_pre_industry
        e.emp_pre_org_name = emp_pre_org_name
        e.emp_pre_desi = emp_pre_desi
        e.emp_prev_tenure = emp_prev_tenure
        e.emp_bank_name = emp_bank_name
        e.emp_account_no = emp_account_no
        e.emp_bank_ifsc = emp_bank_ifsc
        e.emp_aadhar = emp_aadhar
        e.emp_pan = emp_pan
        e.emp_idcard = emp_idcard
        e.emp_certificate = emp_certificate
        e.emp_exp_letter = emp_exp_letter
        e.emp_upload_bank = emp_passbook
        e.added_by = usr_name
        e.save()

    else:
        return render(request,'ams/onboarding.html')

def addNewUserHR(request):
    if request.method == 'POST':

        emp_name = request.POST["emp_name"]
        emp_id = request.POST["emp_id"]
        emp_doj = request.POST["emp_doj"]
        emp_desi = request.POST["emp_desg"]
        emp_rm1 = request.POST["emp_rm1"]
        emp_rm2 = request.POST["emp_rm2"]
        emp_rm3 = request.POST["emp_rm3"]
        emp_process = request.POST["emp_pro"]

        usr = User.objects.filter(username=emp_id)
        if usr.exists():
            return HttpResponse('<h1>User Already Exists</h1>')
        else:
            # Creating User
            user = User.objects.create_user(username=emp_id, password=str(emp_id))

            #Creating Profile
            profile = Profile.objects.create(
                emp_id=emp_id, emp_name=emp_name, emp_desi=emp_desi,
                emp_rm1=emp_rm1, emp_rm2=emp_rm2, emp_rm3=emp_rm3,
                emp_process=emp_process, user_id=user.id,doj=emp_doj,
            )

            #creating Employee table(Mapping)
            emp = Employee.objects.create(
                emp_id=emp_id, emp_name=emp_name, emp_desi=emp_desi,
                emp_rm1=emp_rm1, emp_rm2=emp_rm2, emp_rm3=emp_rm3,
                emp_process=emp_process
            )

        user.save()
        profile.save()
        emp.save()

        messages.info(request,'User and Profile Successfully Created')
        return redirect('/ams/add-new-user')

    else:
        emp_id = request.user.profile.emp_id
        emp = Employee.objects.get(emp_id=emp_id)

        all_desi = Employee.objects.all().values('emp_desi').distinct().order_by('emp_desi')
        rms = Employee.objects.exclude(emp_desi__in =['Client Relationship Officer','Patrolling Officer']).order_by('emp_name')
        all_team = Employee.objects.all().values('emp_process').distinct().order_by('emp_process')
        data = {'emp': emp,'all_data':all_desi,'rms':rms,'all_team':all_team}

        return render(request,'ams/hr_add_user.html',data)

def viewUsersHR(request):
    add = Employee.objects.all()
    data = {'add':add}
    return render(request,'ams/view_user_hr.html',data)

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
        ddate = request.POST['date']
        att_applied = request.POST['att_applied']
        rm1 = request.POST['rm1']
        rm2 = request.POST['rm2']
        rm3 = request.POST['rm3']
        emp_id = request.user.profile.emp_id
        emp_name = request.user.profile.emp_name
        emp_desi = request.user.profile.emp_desi
        team = request.user.profile.emp_process
        now = datetime.now()
        cal = EcplCalander.objects.create(
            team = team, date = ddate, emp_name = emp_name, emp_id = emp_id,
            att_applied = att_applied,applied_by = emp_id,applied_status = True,
            rm1 = rm1, rm2 = rm2, rm3 = rm3,
            applied_on = now, emp_desi = emp_desi,
        )
        cal.save()

        return redirect('/ams/ams-update-attendance')
    else:
        today = date.today()
        yesterday = today - timedelta(days=1)
        dby_date = yesterday - timedelta(days=1)

        emp_name = request.user.profile.emp_name
        emp_id = request.user.profile.emp_id
        emp = Employee.objects.get(emp_id=emp_id)
        try:
            cal_day = EcplCalander.objects.get(date=today, applied_status=True, emp_id=emp_id)
            tdy_date = today
            today = 'Applied'
        except EcplCalander.DoesNotExist:
            today = str(today)
            tdy_date = today

        try:
            cal_yday = EcplCalander.objects.get(date=yesterday, applied_status=True, emp_id=emp_id)
            yst_date = yesterday
            yesterday = 'Applied'

        except EcplCalander.DoesNotExist:
            yst_date = yesterday
            yesterday = str(yesterday)

        try:
            dby = EcplCalander.objects.get(date=dby_date, applied_status=True, emp_id=emp_id)
            dby_date = dby_date
            day_befor_yest = 'Applied'
        except EcplCalander.DoesNotExist:
            dby_date = dby_date
            day_befor_yest = str(dby_date)

        # attendance status
        cal = EcplCalander.objects.filter(emp_id=emp_id).order_by('-date')[:3]

        # Month view
        ########### Month View ############
        month_days = []
        todays_date = date.today()
        year = todays_date.year
        month = todays_date.month
        a, num_days = calendar.monthrange(year, month)
        start_date = date(year, month, 1)
        end_date = date(year, month, num_days)
        delta = timedelta(days=1)
        while start_date <= end_date:
            month_days.append(start_date.strftime("%Y-%m-%d"))
            start_date += delta

        month_cal = []
        for i in month_days:

            dict = {}
            try:
                st = EcplCalander.objects.get(Q(date=i), Q(emp_name=emp_name)).att_actual

            except EcplCalander.DoesNotExist:
                st = 'Unmarked'
            dict['dt'] = i
            dict['st'] = st
            month_cal.append(dict)

        data = {'emp_name': emp_name, 'emp': emp, 'date': today, 'yesterday': yesterday, 'cal': cal,
                'month_cal': month_cal,
                'yst_date': yst_date, 'tdy_date': tdy_date,
                'dby_date': dby_date, 'day_befor_yest': day_befor_yest}

        return render(request,'ams/attendance.html',data)

def rmApproval(request,id):
    if request.method == 'POST':
        usr = request.user.profile.emp_name
        id =id
        now = datetime.now()
        att_approved = request.POST['att_approved']
        att_actual = request.POST['att_actual']
        cal = EcplCalander.objects.get(id=id)
        cal.att_approved = att_approved
        cal.approved_status = True
        cal.approved_on=now
        cal.appoved_by = usr
        cal.att_actual = att_actual
        cal.save()

        return redirect('/ams/view-att-requests')


def attRequests(request):

    emp_name = request.user.profile.emp_name
    id = request.user.profile.emp_id
    cal = EcplCalander.objects.filter(approved_status=False, rm1=emp_name)
    emp = Employee.objects.get(emp_id=id)

    data = {'cal':cal,'emp':emp}
    return render(request,'ams/req_att.html',data)


def agentSettings(request):
    emp_id = request.user.profile.emp_id
    emp = Employee.objects.get(emp_id=emp_id)
    form = PasswordChangeForm(request.user)
    data = {'emp':emp,'form':form}
    return render(request,'ams/agent-settings.html',data)

def rmSettings(request):
    emp_id = request.user.profile.emp_id
    emp = Employee.objects.get(emp_id=emp_id)
    form = PasswordChangeForm(request.user)
    data = {'emp':emp,'form':form}
    return render(request,'ams/rm-settings.html',data)

def uploadImageToDB(request):
    if request.method=='POST':
        user_image = request.FILES['user-img']
        id = request.POST['id']
        prof = Profile.objects.get(id=id)
        prof.img = user_image
        prof.save()

        if request.user.profile.emp_desi in manager_list:
            return redirect('/ams/tl-dashboard')
        else:
            return redirect('/ams/agent-dashboard')

    else:
        pass

def mappingHomePage(request):
    emp_id = request.user.profile.emp_id
    user_nm = request.user.profile.emp_name
    emp = Employee.objects.get(emp_id=emp_id)
    employees = Employee.objects.filter(emp_rm1=user_nm)
    rms = Employee.objects.exclude(emp_desi__in=['Client Relationship Officer', 'Patrolling Officer']).order_by(
        'emp_name')
    teams = Employee.objects.values_list('emp_process', flat=True).distinct()

    data = {'emp': emp,'employees':employees,'rms':rms,'teams':teams}

    return render(request,'ams/mapping_home.html',data)

def createMappingTicket(request):

    if request.method == "POST":
        usr_name = request.user.profile.emp_name
        dt = date.today()

        emp_name = request.POST["emp_name"]
        emp_id = request.POST["emp_id"]
        emp_desi = request.POST["emp_desi"]
        emp_rm1 = request.POST["old_rm1"]
        emp_rm2 = request.POST["old_rm2"]
        emp_rm3 = request.POST["old_rm3"]
        new_rm1 = request.POST["new_rm1"]
        new_rm2 = request.POST["new_rm2"]
        new_rm3 = request.POST["new_rm3"]
        emp_process = request.POST["emp_process"]
        new_process = request.POST["new_process"]
        created_by = usr_name
        created_date = dt
        effective_date = request.POST["effective_date"]

        e = MappingTickets()
        e.emp_name = emp_name
        e.emp_id = emp_id
        e.emp_desi = emp_desi
        e.emp_rm1 = emp_rm1
        e.emp_rm2 = emp_rm2
        e.emp_rm3 = emp_rm3
        e.new_rm1 = new_rm1
        e.new_rm2 = new_rm2
        e.new_rm3 = new_rm3
        e.emp_process = emp_process
        e.new_process = new_process
        e.created_by = created_by
        e.created_date = created_date
        e.effective_date = effective_date
        e.save()

        return redirect('/ams/rm-mapping-index')

    else:
        return redirect('/ams/rm-mapping-index')


@login_required
def viewMappingTicketsHr(request):

    usr = request.user.profile.emp_name
    tickets = MappingTickets.objects.filter(status=False,new_rm3=usr).order_by('created_date')
    emp_id = request.user.profile.emp_id
    emp = Employee.objects.get(emp_id=emp_id)
    data = {'tickets':tickets,'emp':emp}
    return render(request,'ams/view_mapping_tickets.html',data)

@login_required
def approveMappingTicket(request):

    if request.method=='POST':
        usr_name = request.user.profile.emp_name
        id = request.POST['id']
        td = date.today()
        ticket = MappingTickets.objects.get(id=id)
        ticket.status = True
        ticket.approved_by = usr_name
        ticket.approved_date = td
        ticket.save()
        emp_id = ticket.emp_id
        emp = Employee.objects.get(emp_id=emp_id)
        prof = Profile.objects.get(emp_id=emp_id)

        emp.emp_rm1 = ticket.new_rm1
        emp.emp_rm2 = ticket.new_rm2
        emp.emp_rm3 = ticket.new_rm3
        emp.emp_process = ticket.new_process

        emp.save()

        prof.emp_rm1 = ticket.new_rm1
        prof.emp_rm2 = ticket.new_rm2
        prof.emp_rm3 = ticket.new_rm3
        prof.emp_process = ticket.new_process
        prof.save()


        return redirect('/ams/view-mapping-tickets')
    else:
        return redirect('/ams/logout')

