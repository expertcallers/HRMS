import ast
from ctypes.wintypes import PINT
import json
from datetime import datetime, date
import monthdelta
import pytz
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import *
from calendar import Calendar, monthrange
from django.contrib import messages
from datetime import timedelta
import calendar
from datetime import date
from django.db.models import Q, Sum, Max
import xlwt
from .admin import *
from tablib import Dataset

# for converting Numbers to Words
from num2words import num2words

c = Calendar()

# Getting Model from other Apps
from django.apps import apps

Profile = apps.get_model('mapping', 'Profile')
LoginHistory = apps.get_model('mapping', 'LoginHistory')
EmpSeparation = apps.get_model('mapping', 'EmpSeparation')
SOP = apps.get_model('mapping', 'SOP')
SOPAgent = apps.get_model('mapping', 'SOPAgent')
SOPLeader = apps.get_model('mapping', 'SOPLeader')
SOPDataSource = apps.get_model('mapping', 'SOPDataSource')

# TL and AM List
tl_am_list = ['Assistant Manager']
# Manager List
manager_list = []
# HR List
hr_list = []
# Agent List
agent_list = ['Web Developer']
# Management List
management_list = []

rm_list = []
hr_tl_am_list = []
hr_om_list = []
admin_list = []
administration_list = []

ta_list = []

# Create your views here.
def loginPage(request):  # Test1 Test2
    logout(request)
    notice = NoticeECPL.objects.all()
    form = AuthenticationForm()
    data = {'form': form, 'notice': notice}
    return render(request, 'ams/login.html', data)


def view_403(request, exception=None):
    return redirect('/ams/')

def loginAndRedirect(request):  # Test1 Test2

    for i in AccessControl.objects.all():
        if i.access == 'Administration':
            if i.emp_id not in administration_list:
                administration_list.append(i.emp_id)
        elif i.access == 'Admin':
            if i.emp_id not in admin_list:
                admin_list.append(i.emp_id)
    for i in Designation.objects.filter(category__in=['TA', 'TA - TL - AM']):
        if i.name not in ta_list:
            ta_list.append(i.name)

    for i in Designation.objects.filter(category='TL AM'):
        if i.name not in tl_am_list:
            tl_am_list.append(i.name)

    for i in Designation.objects.filter(Q(category='Manager List') | Q(category='Management List')):
        if i.name not in manager_list:
            manager_list.append(i.name)

    for i in Designation.objects.filter(
            Q(category='HR') | Q(category='OM HR') | Q(category='Management List - HR') | Q(category='TL AM HR') | Q(
                category='TA') | Q(category='TA - TL - AM')):
        if i.name not in hr_list:
            hr_list.append(i.name)

    for i in Designation.objects.filter(category='Agent'):
        if i.name not in agent_list:
            agent_list.append(i.name)

    for i in Designation.objects.filter(Q(category='Management List') | Q(category='Management List - HR')):
        if i.name not in management_list:
            management_list.append(i.name)

    for i in Designation.objects.filter(
            Q(category='TL AM') | Q(category='Manager List') | Q(category='OM HR') | Q(category='TL AM HR') | Q(
                category='TA - TL - AM')):
        if i.name not in rm_list:
            rm_list.append(i.name)

    for i in Designation.objects.filter(Q(category='TL AM HR') | Q(category='TA - TL - AM')):
        if i.name not in hr_tl_am_list:
            hr_tl_am_list.append(i.name)

    for i in Designation.objects.filter(Q(category='OM HR') | Q(category='Management List - HR')):
        if i.name not in hr_om_list:
            hr_om_list.append(i.name)

    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if request.user.profile.agent_status == "Active":
                if request.user.profile.pc == False:
                    return redirect('/ams/change-password')
                else:
                    return redirect('/ams/dashboard-redirect')
            else:
                messages.info(request, 'You are Inactive. Please contact HR.')
                return redirect("/ams/")
        else:
            messages.info(request, 'Invalid Credentials')
            return redirect("/ams/")
    else:
        return redirect("/ams/")


@login_required
def redirectTOAllDashBoards(request):  # Test1 Test2
    if request.user.profile.emp_desi in tl_am_list:
        return redirect('/ams/tl-dashboard')
    elif request.user.profile.emp_desi in hr_list:
        return redirect('/ams/hr-dashboard')
    elif request.user.profile.emp_desi in manager_list:
        return redirect('/ams/manager-dashboard')
    elif request.user.profile.emp_desi in agent_list:
        return redirect('/ams/agent-dashboard')
    else:
        messages.info(request, 'Not Authorised to view this page')
        return redirect("/ams/")


def logoutView(request):  # Test1 Test2
    logout(request)
    return redirect('/ams/')


@login_required
def change_password(request):  # Test1 Test2
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            user = request.user
            user.profile.pc = True
            user.save()
            user.profile.save()
            logout(request)
            return redirect('/ams/')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'ams/change-password.html', {'form': form})


@login_required
def getEmp(request):
    emp_id = request.POST['emp_id']
    profile = Profile.objects.get(emp_id=emp_id)
    prof_dict = {}
    prof_dict['emp_name'] = profile.emp_name
    prof_dict['emp_id'] = profile.emp_id
    prof_dict['emp_desi'] = profile.emp_desi
    prof_dict['emp_process'] = profile.emp_process
    prof_dict['img'] = str(profile.img)
    prof_dict['doj'] = str(profile.doj)
    return HttpResponse(json.dumps(prof_dict))

@login_required
def agentDashBoard(request):  # Test1 Test2 # Opt
    if request.user.profile.emp_desi in agent_list:
        emp = request.user.profile
        birthdays = getBirthdays()
        leave_hist = LeaveTable.objects.filter(Q(emp_id=emp.emp_id), Q(leave_type__in=['SL', 'PL', 'ML'])).order_by('-id')[:5]

        new_joins = Profile.objects.all().order_by('-id')[:5]
        data = {'emp': emp, 'leave_hist': leave_hist, 'admin_list': admin_list,
                'administration_list': administration_list, 'birthdays': birthdays, 'new_joins': new_joins}
        return render(request, 'ams/agent-dashboard-new.html', data)
    else:
        return HttpResponse('<H1>You are not Authorised to view this page ! </H1>')

@login_required
def tlDashboard(request):  # Test1 Test2
    usr_desi = request.user.profile.emp_desi
    if usr_desi in tl_am_list:
        prof = request.user.profile
        emp_id = prof.emp_id    
        # All Employees # Used in dropdown attendance report
        all_emp = Profile.objects.filter(Q(agent_status='Active'),Q(emp_id=emp_id) | Q(emp_rm1_id=emp_id) | Q(emp_rm2_id=emp_id) | Q(emp_rm3_id=emp_id)).distinct()
        # All Active Today
        today = date.today()
        # All team members attendance details
        emps = Profile.objects.filter(Q(emp_rm1_id=emp_id), Q(agent_status='Active')).values('emp_id')
        att_details = EcplCalander.objects.filter(Q(date=today), Q(emp_id__in=emps))        
        # counts
        emp_count = all_emp.count()-1
        # Mapping Tickets 
        map_tickets_counts = MappingTickets.objects.filter(new_rm3_id=emp_id, status=False).count()
        # Leaves
        leave_req_count = LeaveTable.objects.filter(emp_rm1_id=emp_id, tl_approval=False).count()
        # Add Comment
        emps = Profile.objects.filter(Q(emp_rm3_id=emp_id) | Q(emp_rm2_id=emp_id) | Q(emp_rm1_id=emp_id))
        rm3 = ""
        for i in emps:
            if i.emp_rm3_id == emp_id:
                rm3 = "yes"
                break
        profile = request.user.profile
        # Check in start
        login = False
        login_id = None
        try:
            login = LoginHistory.objects.filter(profile=profile, done=False).order_by('id')[:1]
            if login:
                for i in login:
                    login_id = i.id
                    login = str(i.login)
            else:
                login = False
                login_id = None
        except LoginHistory.DoesNotExist:
            pass
        try:
            login = LoginHistory.objects.get(profile=profile, date=date.today(), done=True)
            login_id = datetime.strptime(str(login.logout - login.login), "%H:%M:%S.%f")
            login_id = (login_id).strftime("%H:%M:%S")
            login = True
        except LoginHistory.DoesNotExist:
            pass

        new_joins = Profile.objects.all().order_by('-id')[:5]


        birthdays = getBirthdays()

        exit_req_count = EmpSeparation.objects.filter(
            Q(profile__emp_rm1_id=emp_id) | Q(profile__emp_rm2_id=emp_id) | Q(profile__emp_rm3_id=emp_id)).count()

        data = {'emp': prof, 'att_details': att_details, 'emp_count': emp_count,
                'map_tickets_counts': map_tickets_counts,'all_emp': all_emp, 'leave_req_count': leave_req_count,
                "rm3": rm3, 'admin_list': admin_list, 'administration_list': administration_list,
                'login': login, 'login_id': login_id, 'new_joins': new_joins, 'birthdays': birthdays,
                'exit_req_count': exit_req_count,}
        return render(request, 'ams/rm-dashboard-new.html', data)

    elif usr_desi in manager_list:
        return redirect('/ams/manager-dashboard')
    elif usr_desi in hr_list:
        return redirect('/ams/hr-dashboard')
    elif usr_desi in agent_list:
        return redirect('/ams/agent-dashboard')
    else:
        messages.error(request, "You are not Authorised to view this page! You have been Logged Out! ")
        return redirect('/ams/')

def getBirthdays():
    # Birthday Start
    start = date.today()
    end = start + timedelta(days=30)
    emps = Profile.objects.exclude(agent_status__in=['Attrition', 'Attrition Duplicate', 'NCNS'])
    emp_ids = []
    for i in emps:
        emp_ids.append(i.emp_id)
    this_month = OnboardingnewHRC.objects.filter(emp_id__in=emp_ids, emp_dob__month=start.month)
    next_month = OnboardingnewHRC.objects.filter(emp_id__in=emp_ids, emp_dob__month=end.month)
    birthdays = []

    def birthdayCreator(mnth, yr):
        for i in mnth:
            dic = {}
            dic['profile'] = Profile.objects.filter(emp_id=i.emp_id).first()
            dic['dob'] = i.emp_dob.replace(year=yr)
            birthdays.append(dic)

    birthdayCreator(this_month, start.year)
    birthdayCreator(next_month, end.year)
    birthdays = sorted(birthdays, key=lambda x: x['dob'])
    new_birthdays = []
    for i in birthdays:
        if i['dob'] >= date.today() and i['dob'] <= date.today()+timedelta(days=30):
            new_birthdays.append(i)
    return new_birthdays
    # Birthday End

@login_required
def managerDashboard(request):  # Test1 Test2
    emp = request.user.profile
    emp_id = emp.emp_id
    # Mapping Tickets
    map_tickets_counts = MappingTickets.objects.filter(new_rm3_id=emp_id, status=False).count()
    # Leave Requests
    leave_req_count = LeaveTable.objects.filter(emp_rm3_id=emp_id, tl_status='Approved', manager_approval=False).count()
    # Leave Escalation Count
    leave_esc_count = LeaveTable.objects.filter(emp_rm3_id=emp_id, manager_approval=False, escalation=True).count()
    # Attendance
    att_requests_count = AttendanceCorrectionHistory.objects.filter(status=False, rm3_id=emp_id).count()   

    if request.user.profile.emp_desi in management_list and request.user.profile.emp_desi in manager_list:
        # All Employees
        all_emps = Profile.objects.filter(Q(agent_status='Active'),Q(emp_id=emp_id) | Q(emp_rm1_id=emp_id) | Q(emp_rm2_id=emp_id) | Q(emp_rm3_id=emp_id)).distinct()
        all_emps_under = []
        for i in all_emps:
            if i not in all_emps_under:
                all_emps_under.append(i)
                under = Profile.objects.filter(Q(agent_status='Active'),Q(emp_rm1_id=i.emp_id) | Q(emp_rm2_id=i.emp_id) | Q(emp_rm3_id=i.emp_id))
                for j in under:
                    if j not in all_emps_under:
                        all_emps_under.append(j)
        # count of all employees
        count_all_emps = len(all_emps_under)
        # TLS
        all_tls_under = []
        for i in all_emps_under:
            if i not in all_tls_under:
                if i.emp_desi == 'Team Leader':
                    all_tls_under.append(i)
        # TLS Count
        all_tls_count = len(all_tls_under)
        # AMS
        all_ams_under = []
        for i in all_emps_under:
            if i not in all_ams_under:
                if i.emp_desi == 'Assistant Manager':
                    all_ams_under.append(i)
        # AMS Count
        all_ams_count = len(all_ams_under)
    elif request.user.profile.emp_desi in manager_list:
        # All Employees
        all_emps = Profile.objects.filter(Q(agent_status='Active'),Q(emp_id=emp_id) | Q(emp_rm1_id=emp_id) | Q(emp_rm2_id=emp_id) | Q(emp_rm3_id=emp_id)).distinct()
        all_emps_under = []
        for i in all_emps:
            if i not in all_emps_under:
                all_emps_under.append(i)
        # count of all employees
        count_all_emps = all_emps.count()
        # TLS
        all_tls = Profile.objects.filter(Q(agent_status='Active'),Q(emp_rm1_id=emp_id) | Q(emp_rm2_id=emp_id) | Q(emp_rm3_id=emp_id),Q(emp_desi='Team Leader')).distinct()
        all_tls_under = list(all_tls)

        # TLS Count
        all_tls_count = all_tls.count()
        # AMS
        all_ams = Profile.objects.filter(Q(agent_status='Active'),Q(emp_rm1_id=emp_id) | Q(emp_rm2_id=emp_id) | Q(emp_rm3_id=emp_id),Q(emp_desi='Assistant Manager')).distinct()
        all_ams_under = list(all_ams)
        # TLS Count
        all_ams_count = all_ams.count()
    else:
        messages.error(request, "You are not Authorised to view this page! You have been Logged Out! ")
        return redirect('/ams')

    birthdays = getBirthdays()
    new_joins = Profile.objects.all().order_by('-id')[:5]
    exit_req_count = EmpSeparation.objects.filter(
        Q(profile__emp_rm1_id=emp_id) | Q(profile__emp_rm2_id=emp_id) | Q(profile__emp_rm3_id=emp_id)).count()

    data = {'emp': emp, 'count_all_emps': count_all_emps, 'all_tls': all_tls_under, 'all_tls_count': all_tls_count,
            'all_ams': all_ams_under, 'all_ams_count': all_ams_count,
            'map_tickets_counts': map_tickets_counts, 'att_requests_count': att_requests_count,
            'leave_req_count': leave_req_count, 'leave_esc_count': leave_esc_count, 'all_emp': all_emps_under,
            'admin_list': admin_list, 'administration_list': administration_list, 'birthdays': birthdays,
            'new_joins': new_joins, 'exit_req_count': exit_req_count,
            }
    return render(request, 'ams/manager-dashboard.html', data)

@login_required
def viewAndApproveLeaveRequestMgr(request):  # Test1
    if request.method == 'POST':
        id = request.POST["id"]
        e = LeaveTable.objects.get(id=id)
        emp_id = e.emp_id
        team = e.emp_process
        att_actual = e.leave_type
        leave_type = e.leave_type
        no_days = e.no_days
        rm1 = e.emp_rm1
        rm2 = e.emp_rm2
        rm3 = e.emp_rm3
        emp_desi = e.emp_desi
        emp_name = e.emp_name
        now = datetime.now()
        start_date = e.start_date
        end_date = e.end_date
        om_response = request.POST['tl_response']
        om_reason = request.POST['tl_reason']
        if om_response == 'Approve':
            if e.start_date < date(date.today().year, date.today().month, 1):
                messages.error(request, 'Previous Month Leaves cannot be approved in this month.')
                return redirect('/ams/view-leave-request-mgr')
            else:
                manager_approval = True
                manager_status = 'Approved'
                status = 'Approved'
                month_days = []
                start_date = start_date
                end_date = end_date
                delta = timedelta(days=1)
                while start_date <= end_date:
                    month_days.append(start_date.strftime("%Y-%m-%d"))
                    start_date += delta
                for i in month_days:
                    try:
                        cal = EcplCalander.objects.get(Q(date=i), Q(emp_id=emp_id))
                        cal.att_actual = att_actual
                        cal.appoved_by = request.user.profile.emp_name
                        cal.approved_on = now
                        cal.unique_id = 'Leave Approval'
                        cal.save()
                    except EcplCalander.DoesNotExist:
                        cal = EcplCalander.objects.create(
                            team=team, date=i, emp_id=emp_id,
                            att_actual=att_actual,
                            rm1=rm1, rm2=rm2, rm3=rm3,
                            rm1_id=e.emp_rm1_id, rm2_id=e.emp_rm2_id, rm3_id=e.emp_rm3_id,
                            approved_on=now, emp_desi=emp_desi, appoved_by=request.user.profile.emp_name,
                            emp_name=emp_name, unique_id='Leave Approval',
                        )
                        cal.save()
        else:
            manager_approval = True
            manager_status = 'Rejected'
            status = 'Rejected'
            leave_balance = EmployeeLeaveBalance.objects.get(emp_id=emp_id)
            if leave_type == 'PL':
                leave_balance.pl_balance += int(no_days)
                leave_balance.save()
            elif leave_type == 'SL':
                leave_balance.sl_balance += int(no_days)
                leave_balance.save()

            leave_history = leaveHistory()
            leave_history.leave_type = leave_type
            leave_history.transaction = 'Leave Refund as RM3 Rejected, Leave applied on: ' + str(
                e.applied_date) + ' (ID: ' + str(e.id) + ')'
            leave_history.date = date.today()
            leave_history.no_days = int(no_days)
            leave_history.emp_id = emp_id
            pl = EmployeeLeaveBalance.objects.get(emp_id=emp_id).pl_balance
            sl = EmployeeLeaveBalance.objects.get(emp_id=emp_id).sl_balance
            leave_history.total = pl + sl
            leave_history.save()

        e.manager_approval = manager_approval
        e.manager_reason = om_reason
        e.manager_date = datetime.now()
        e.manager_status = manager_status
        e.status = status
        e.save()
        return redirect('/ams/dashboard-redirect')
    else:

        emp_id = request.user.profile.emp_id
        emp = Profile.objects.get(emp_id=emp_id)
        leave_request = LeaveTable.objects.filter(Q(emp_rm3_id=emp_id), Q(tl_status='Approved'),
                                                  Q(manager_approval=False))
        data = {'emp': emp, 'leave_request': leave_request}
        return render(request, 'ams/leave_approval_rm3.html', data)


@login_required
def viewallOMS(request, name):  # Test1
    emp_id = request.user.profile.emp_id
    emp = Profile.objects.get(emp_id=emp_id)
    all_emp = Profile.objects.filter(Q(agent_status='Active'),
                                     Q(emp_rm1_id=emp_id) | Q(emp_rm2_id=emp_id) | Q(emp_rm3_id=emp_id))
    all_emps_under = []
    for i in all_emp:
        if i not in all_emps_under:
            all_emps_under.append(i)
            under = Profile.objects.filter(Q(agent_status='Active'),
                                           Q(emp_rm1_id=i.emp_id) | Q(emp_rm2_id=i.emp_id) | Q(emp_rm3_id=i.emp_id))
            for j in under:
                if j not in all_emps_under:
                    all_emps_under.append(j)
    if name == 'Agent':
        all_emps_under = all_emps_under
        data = {'emp': emp, 'all_emp': all_emps_under}
        return render(request, 'ams/view_all_emp_om.html', data)
    elif name == 'TL':
        all_tls_under = []
        for i in all_emps_under:
            if i not in all_tls_under:
                if i.emp_desi == 'Team Leader':
                    all_tls_under.append(i)
        data = {'emp': emp, 'all_emp': all_tls_under}
        return render(request, 'ams/view_all_emp_om.html', data)
    elif name == 'AM':
        all_ams_under = []
        for i in all_emps_under:
            if i not in all_ams_under:
                if i.emp_desi == 'Assistant Manager':
                    all_ams_under.append(i)
        data = {'emp': emp, 'all_emp': all_ams_under}
        return render(request, 'ams/view_all_emp_om.html', data)
    else:
        messages.info(request, 'Bad Request')
        return redirect('/ams/manager-dashboard')


@login_required
def hrDashboard(request):  # Test1
    user_desi = request.user.profile.emp_desi
    if user_desi in hr_list:
        emp = request.user.profile
        emp_id = emp.emp_id
        all_users_count = Profile.objects.all().count()
        all_team_count = Campaigns.objects.all().count()
        teams = Campaigns.objects.all()
        # Leave Requests
        leave_req_count = LeaveTable.objects.filter(emp_rm1_id=emp_id, tl_approval=False).count()
        leave_req_count_final = LeaveTable.objects.filter(emp_rm3_id=emp_id, tl_status='Approved',manager_approval=False).count()
        # Mapping Tickets
        map_tickets_counts = MappingTickets.objects.filter(Q(new_rm3_id=emp_id), Q(status=False)).count()
        # Leave Escalation Count
        leave_esc_count = LeaveTable.objects.filter(Q(emp_rm3_id=emp_id), Q(manager_approval=False),Q(escalation=True)).count()
        # Attendance
        att_requests_count = AttendanceCorrectionHistory.objects.filter(status=False, rm3_id=emp_id).count()

        birthdays = getBirthdays()

        new_joins = Profile.objects.all().order_by('-id')[:5]
        data = {'emp': emp, 'all_users_count': all_users_count, 'all_team_count': all_team_count,
                "leave_req_count": leave_req_count, "map_tickets_counts": map_tickets_counts,
                "leave_esc_count": leave_esc_count, "att_requests_count": att_requests_count,
                "hr_tl_am_list": hr_tl_am_list, "hr_om_list": hr_om_list,
                "leave_req_count_final": leave_req_count_final, 'admin_list': admin_list,
                'administration_list': administration_list, 'team': teams, 'ta': ta_list, 'birthdays': birthdays,
                'new_joins': new_joins}
        return render(request, 'ams/hr_dashboard.html', data)
    else:
        return HttpResponse('<h1>*** You are not authorised to view this page ***</h1>')


@login_required
def on_boarding(request):  # Test1
    if request.method == "POST":
        hrname = request.user
        emp_id = request.POST["profile"]
        emp_name = request.POST["emp_name"]
        emp_dob = request.POST["emp_dob"]
        emp_desig = request.POST["emp_desg"]
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
        emp_blood = request.POST["emp_blo"]
        emp_emergency_person = request.POST["emp_emer_name"]
        emp_emergency_number = request.POST["emp_emer_ph"]
        emp_emergency_address = request.POST["emp_emer_add"]
        emp_emergency_person2 = request.POST["emp_emer_name2"]
        emp_emergency_number2 = request.POST["emp_emer_ph2"]
        emp_emergency_address2 = request.POST["emp_emer_add2"]
        emp_edu_qualification = request.POST["emp_high_qua"]
        emp_quali_other = request.POST["other_quli"]
        emp_edu_course = request.POST["emp_cou"]
        emp_edu_institute = request.POST["emp_ins"]
        # Previous Experience
        emp_pre_exp = request.POST["emp_exp"]
        emp_pre_industry = request.POST.get("emp_ind")
        emp_pre_org_name = request.POST["emp_pre_org"]
        emp_pre_desg = request.POST["emp_pre_desg"]
        emp_pre_period_of_employment_frm = request.POST["emp_pre_empl_from"]
        emp_pre_period_of_employment_to = request.POST["emp_pre_empl_to"]
        emp_pre_exp_two = request.POST.get("emp_exp_2")
        emp_pre_industry_two = request.POST.get("emp_ind_2")
        emp_pre_org_name_two = request.POST.get("emp_pre_org_2")
        emp_pre_desg_two = request.POST.get("emp_pre_desg_2")
        emp_pre_period_of_employment_frm_two = request.POST.get("emp_pre_empl_from_2")
        emp_pre_period_of_employment_to_two = request.POST.get("emp_pre_empl_to_2")
        emp_pre_exp_three = request.POST.get("emp_exp_3")
        emp_pre_industry_three = request.POST.get("emp_ind_3")
        emp_pre_org_name_three = request.POST.get("emp_pre_org_3")
        emp_pre_desg_three = request.POST.get("emp_pre_desg_3")
        emp_pre_period_of_employment_frm_three = request.POST.get("emp_pre_empl_from_3")
        emp_pre_period_of_employment_to_three = request.POST.get("emp_pre_empl_to_3")
        # Bank
        emp_bank_holder_name = request.POST["emp_bank_name"]
        emp_bank_name = request.POST["emp_bank_na"]
        emp_bank_acco_no = request.POST["emp_bank_no"]
        emp_bank_ifsc = request.POST["emp_bank_ifsc"]  #
        have_system = request.POST["have_system"]
        require_system = request.POST["require_system"]
        wifi_broadband = request.POST["wifi"]
        emp_upload_aadhar = request.FILES.get("emp_up_aad")
        emp_upload_aadhar_back = request.FILES.get("emp_up_aad_back")
        emp_upload_pan = request.FILES.get("emp_up_pan")
        emp_upload_id = request.FILES.get("emp_up_id")
        emp_upload_id_back = request.FILES.get("emp_up_id_back")
        emp_upload_edu_sslc = request.FILES.get("emp_up_edu")
        emp_upload_edu_twelveth = request.FILES.get("emp_up_edu_12")
        emp_upload_edu_gradu = request.FILES.get("emp_up_edu_gra")
        emp_upload_experience = request.FILES.get("emp_up_cer")
        emp_upload_experience_two = request.FILES.get("emp_up_cer_2")
        emp_upload_experience_three = request.FILES.get("emp_up_cer_3")
        emp_upload_bank = request.FILES.get("emp_up_bank")
        esic = request.POST["esic"]
        pf = request.POST["pf"]
        tds = request.POST["tds"]
        pt = request.POST["pt"]
        e = OnboardingnewHRC()
        e.esic = esic
        e.pf = pf
        e.tds = tds
        e.pt = pt
        e.submit_date = datetime.now()
        e.emp_name = emp_name
        e.emp_dob = emp_dob
        e.emp_desig = emp_desig
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
        e.emp_blood = emp_blood
        e.emp_emergency_person = emp_emergency_person
        e.emp_emergency_number = emp_emergency_number
        e.emp_emergency_address = emp_emergency_address
        e.emp_emergency_person_two = emp_emergency_person2
        e.emp_emergency_number_two = emp_emergency_number2
        e.emp_emergency_address_two = emp_emergency_address2
        e.emp_edu_qualification = emp_edu_qualification
        e.emp_quali_other = emp_quali_other
        e.emp_edu_course = emp_edu_course
        e.emp_edu_institute = emp_edu_institute
        # emp pevious experiance
        e.emp_pre_exp = emp_pre_exp
        e.emp_pre_industry = emp_pre_industry
        e.emp_pre_org_name = emp_pre_org_name
        e.emp_pre_desg = emp_pre_desg
        if emp_pre_period_of_employment_frm:
            e.emp_pre_period_of_employment_frm = emp_pre_period_of_employment_frm
        if emp_pre_period_of_employment_to:
            e.emp_pre_period_of_employment_to = emp_pre_period_of_employment_to
        if emp_pre_exp_two:
            e.emp_pre_exp_two = emp_pre_exp_two
        if emp_pre_industry_two:
            e.emp_pre_industry_two = emp_pre_industry_two
        if emp_pre_org_name_two:
            e.emp_pre_org_name_two = emp_pre_org_name_two
        if emp_pre_desg_two:
            e.emp_pre_desg_two = emp_pre_desg_two
        if emp_pre_period_of_employment_frm_two:
            e.emp_pre_period_of_employment_frm_two = emp_pre_period_of_employment_frm_two
        if emp_pre_period_of_employment_to_two:
            e.emp_pre_period_of_employment_to_two = emp_pre_period_of_employment_to_two
        if emp_pre_exp_three:
            e.emp_pre_exp_three = emp_pre_exp_three
        if emp_pre_industry_three:
            e.emp_pre_industry_three = emp_pre_industry_three
        if emp_pre_org_name_three:
            e.emp_pre_org_name_three = emp_pre_org_name_three
        if emp_pre_desg_three:
            e.emp_pre_desg_three = emp_pre_desg_three
        if emp_pre_period_of_employment_frm_three:
            e.emp_pre_period_of_employment_frm_three = emp_pre_period_of_employment_frm_three
        if emp_pre_period_of_employment_to_three:
            e.emp_pre_period_of_employment_to_three = emp_pre_period_of_employment_to_three
        e.emp_bank_holder_name = emp_bank_holder_name
        e.emp_bank_name = emp_bank_name
        e.emp_bank_acco_no = emp_bank_acco_no
        e.emp_bank_ifsc = emp_bank_ifsc
        e.have_system = have_system
        e.require_system = require_system
        e.wifi_broadband = wifi_broadband
        e.emp_upload_aadhar = emp_upload_aadhar
        e.emp_upload_aadhar_back = emp_upload_aadhar_back
        e.emp_upload_pan = emp_upload_pan
        e.emp_upload_id = emp_upload_id
        e.emp_upload_id_back = emp_upload_id_back
        e.emp_upload_edu_sslc = emp_upload_edu_sslc
        e.emp_upload_edu_twelveth = emp_upload_edu_twelveth
        e.emp_upload_edu_gradu = emp_upload_edu_gradu
        e.emp_upload_experience = emp_upload_experience
        e.emp_upload_experience_two = emp_upload_experience_two
        e.emp_upload_experience_three = emp_upload_experience_three
        e.emp_upload_bank = emp_upload_bank
        e.hr_name = hrname
        e.emp_id = emp_id
        e.save()
        profile = Profile.objects.get(emp_id=emp_id)
        profile.on_id = e.id
        profile.save()
        return redirect("/ams/onboarding")
    else:
        profiles = Profile.objects.filter(Q(on_id=None)).order_by('-id')
        today_date = date.today()
        minimum_dob = today_date - timedelta(days=6588)
        emp_id = request.user.profile.emp_id
        emp = Profile.objects.get(emp_id=emp_id)
        data = {'emp': emp, 'minimum_dob': str(minimum_dob), 'profiles': profiles, 'hr_om_list': hr_om_list,
                'hr_tl_am_list': hr_tl_am_list}
        return render(request, 'ams/onboarding.html', data)


@login_required
def viewOnBoarding(request):  # Test1
    profiles = Profile.objects.filter(~Q(on_id=None))
    onboard = OnboardingnewHRC.objects.all()
    emp_id = request.user.profile.emp_id
    emp = Profile.objects.get(emp_id=emp_id)
    data = {'onboard': onboard, 'emp': emp, 'hr_om_list': hr_om_list, 'hr_tl_am_list': hr_tl_am_list}
    return render(request, "ams/view_onboarding.html", data)


@login_required
def on_boarding_update(request, id):  # Test1
    if request.method == "POST":
        id = request.POST["id"]
        e = OnboardingnewHRC.objects.get(id=id)
        hrname = request.user.profile.emp_id
        hrname = User.objects.get(username=hrname)
        emp_name = request.POST["emp_name"]
        emp_dob = request.POST["emp_dob"]
        emp_desig = request.POST["emp_desg"]
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
        emp_blood = request.POST["emp_blo"]
        emp_emergency_person = request.POST["emp_emer_name"]
        emp_emergency_number = request.POST["emp_emer_ph"]
        emp_emergency_address = request.POST["emp_emer_add"]
        emp_emergency_person2 = request.POST["emp_emer_name2"]
        emp_emergency_number2 = request.POST["emp_emer_ph2"]
        emp_emergency_address2 = request.POST["emp_emer_add2"]
        emp_edu_qualification = request.POST["emp_high_qua"]
        emp_quali_other = request.POST["other_quli"]
        emp_edu_course = request.POST["emp_cou"]
        emp_edu_institute = request.POST["emp_ins"]
        # Previous Experience
        emp_pre_exp = request.POST["emp_exp"]
        emp_pre_industry = request.POST.get("emp_ind")
        emp_pre_org_name = request.POST["emp_pre_org"]
        emp_pre_desg = request.POST["emp_pre_desg"]
        emp_pre_period_of_employment_frm = request.POST.get("emp_pre_empl_from")
        emp_pre_period_of_employment_to = request.POST.get("emp_pre_empl_to")
        emp_pre_exp_two = request.POST.get("emp_exp_2")
        emp_pre_industry_two = request.POST.get("emp_ind_2")
        emp_pre_org_name_two = request.POST.get("emp_pre_org_2")
        emp_pre_desg_two = request.POST.get("emp_pre_desg_2")
        emp_pre_period_of_employment_frm_two = request.POST.get("emp_pre_empl_from_2")
        emp_pre_period_of_employment_to_two = request.POST.get("emp_pre_empl_to_2")
        emp_pre_exp_three = request.POST.get("emp_exp_3")
        emp_pre_industry_three = request.POST.get("emp_ind_3")
        emp_pre_org_name_three = request.POST.get("emp_pre_org_3")
        emp_pre_desg_three = request.POST.get("emp_pre_desg_3")
        emp_pre_period_of_employment_frm_three = request.POST.get("emp_pre_empl_from_3")
        emp_pre_period_of_employment_to_three = request.POST.get("emp_pre_empl_to_3")
        # Bank
        emp_bank_holder_name = request.POST["emp_bank_name"]
        emp_bank_name = request.POST["emp_bank_na"]
        emp_bank_acco_no = request.POST["emp_bank_no"]
        emp_bank_ifsc = request.POST["emp_bank_ifsc"]
        have_system = request.POST["have_system"]
        require_system = request.POST["require_system"]
        wifi_broadband = request.POST["wifi"]
        emp_upload_aadhar = request.FILES.get("emp_up_aad")
        emp_upload_aadhar_back = request.FILES.get("emp_up_aad_back")
        emp_upload_pan = request.FILES.get("emp_up_pan")
        emp_upload_id = request.FILES.get("emp_up_id")
        emp_upload_id_back = request.FILES.get("emp_up_id_back")
        emp_upload_edu_sslc = request.FILES.get("emp_up_edu")
        emp_upload_edu_twelveth = request.FILES.get("emp_up_edu_12")
        emp_upload_edu_gradu = request.FILES.get("emp_up_edu_gra")
        emp_upload_experience = request.FILES.get("emp_up_cer")
        emp_upload_experience_two = request.FILES.get("emp_up_cer_2")
        emp_upload_experience_three = request.FILES.get("emp_up_cer_3")
        emp_upload_bank = request.FILES.get("emp_up_bank")
        esic = request.POST["esic"]
        pf = request.POST["pf"]
        tds = request.POST["tds"]
        pt = request.POST["pt"]
        e.esic = esic
        e.pf = pf
        e.tds = tds
        e.pt = pt
        e.emp_name = emp_name
        e.emp_dob = emp_dob
        e.emp_desig = emp_desig
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
        e.emp_blood = emp_blood
        e.emp_emergency_person = emp_emergency_person
        e.emp_emergency_number = emp_emergency_number
        e.emp_emergency_address = emp_emergency_address
        e.emp_emergency_person_two = emp_emergency_person2
        e.emp_emergency_number_two = emp_emergency_number2
        e.emp_emergency_address_two = emp_emergency_address2
        e.emp_edu_qualification = emp_edu_qualification
        e.emp_quali_other = emp_quali_other
        e.emp_edu_course = emp_edu_course
        e.emp_edu_institute = emp_edu_institute
        # emp pevious experiance
        e.emp_pre_exp = emp_pre_exp
        e.emp_pre_industry = emp_pre_industry
        e.emp_pre_org_name = emp_pre_org_name
        e.emp_pre_desg = emp_pre_desg
        if emp_pre_period_of_employment_frm:
            e.emp_pre_period_of_employment_frm = emp_pre_period_of_employment_frm
        if emp_pre_period_of_employment_to:
            e.emp_pre_period_of_employment_to = emp_pre_period_of_employment_to
        if emp_pre_exp_two:
            e.emp_pre_exp_two = emp_pre_exp_two
        if emp_pre_industry_two:
            e.emp_pre_industry_two = emp_pre_industry_two
        if emp_pre_org_name_two:
            e.emp_pre_org_name_two = emp_pre_org_name_two
        if emp_pre_desg_two:
            e.emp_pre_desg_two = emp_pre_desg_two
        if emp_pre_period_of_employment_frm_two:
            e.emp_pre_period_of_employment_frm_two = emp_pre_period_of_employment_frm_two
        if emp_pre_period_of_employment_to_two:
            e.emp_pre_period_of_employment_to_two = emp_pre_period_of_employment_to_two
        if emp_pre_exp_three:
            e.emp_pre_exp_three = emp_pre_exp_three
        if emp_pre_industry_three:
            e.emp_pre_industry_three = emp_pre_industry_three
        if emp_pre_org_name_three:
            e.emp_pre_org_name_three = emp_pre_org_name_three
        if emp_pre_desg_three:
            e.emp_pre_desg_three = emp_pre_desg_three
        if emp_pre_period_of_employment_frm_three:
            e.emp_pre_period_of_employment_frm_three = emp_pre_period_of_employment_frm_three
        if emp_pre_period_of_employment_to_three:
            e.emp_pre_period_of_employment_to_three = emp_pre_period_of_employment_to_three
        e.emp_bank_holder_name = emp_bank_holder_name
        e.emp_bank_name = emp_bank_name
        e.emp_bank_acco_no = emp_bank_acco_no
        e.emp_bank_ifsc = emp_bank_ifsc
        e.have_system = have_system
        e.require_system = require_system
        e.wifi_broadband = wifi_broadband
        if emp_upload_aadhar:
            e.emp_upload_aadhar = emp_upload_aadhar
        if emp_upload_aadhar_back:
            e.emp_upload_aadhar_back = emp_upload_aadhar_back
        if emp_upload_pan:
            e.emp_upload_pan = emp_upload_pan
        if emp_upload_id:
            e.emp_upload_id = emp_upload_id
        if emp_upload_id_back:
            e.emp_upload_id_back = emp_upload_id_back
        if emp_upload_edu_sslc:
            e.emp_upload_edu_sslc = emp_upload_edu_sslc
        if emp_upload_edu_twelveth:
            e.emp_upload_edu_twelveth = emp_upload_edu_twelveth
        if emp_upload_edu_gradu:
            e.emp_upload_edu_gradu = emp_upload_edu_gradu
        if emp_upload_experience:
            e.emp_upload_experience = emp_upload_experience
        if emp_upload_experience_two:
            e.emp_upload_experience_two = emp_upload_experience_two
        if emp_upload_experience_three:
            e.emp_upload_experience_three = emp_upload_experience_three
        if emp_upload_bank:
            e.emp_upload_bank = emp_upload_bank
        e.hr_name = hrname
        e.save()
        return redirect("/ams/view-onboarding")
    else:
        id = id
        onboard = OnboardingnewHRC.objects.get(id=id)
        emp_id = request.user.profile.emp_id
        today_date = date.today()
        minimum_dob = today_date - timedelta(days=6588)
        emp = Profile.objects.get(emp_id=emp_id)
        data = {"onboard": onboard, 'emp': emp, 'minimum_dob': str(minimum_dob)}
        return render(request, "ams/edit_onboarding.html", data)


@login_required
def addNewUserHR(request):  # Test1  # calander pending
    if request.method == 'POST':
        emp_name = request.POST["emp_name"]
        emp_id = request.POST["emp_id"]
        emp_doj = request.POST["emp_doj"]
        emp_desi = request.POST["emp_desg"]
        emp_rm1_id = request.POST["emp_rm1_id"]
        emp_rm2_id = request.POST["emp_rm2_id"]
        emp_rm3_id = request.POST["emp_rm3_id"]
        emp_rm1 = Profile.objects.get(emp_id=emp_rm1_id)
        emp_rm2 = Profile.objects.get(emp_id=emp_rm2_id)
        emp_rm3 = Profile.objects.get(emp_id=emp_rm3_id)
        emp_process_id = request.POST["emp_pro"]
        emp_process = Campaigns.objects.get(id=emp_process_id).name
        usr = User.objects.filter(username=emp_id)
        if usr.exists():
            messages.info(request, "***User Already Exists***")
            return redirect("/ams/add-new-user")
        else:
            # Creating User
            user = User.objects.create_user(username=emp_id, password=str(emp_id))
            # Creating Profile
            Profile.objects.create(
                user=user, emp_id=emp_id, emp_name=emp_name, emp_desi=emp_desi,
                emp_rm1=emp_rm1, emp_rm2=emp_rm2, emp_rm3=emp_rm3, emp_rm1_id=emp_rm1_id, emp_rm2_id=emp_rm2_id,
                emp_rm3_id=emp_rm3_id, emp_process=emp_process, emp_process_id=emp_process_id, doj=emp_doj,
            )
            # Updating Last Emp ID
            profiles = Profile.objects.all().order_by('-id')
            int_emp_id_lst = []
            for i in profiles:
                try:
                    j = int(i.emp_id)
                    int_emp_id_lst.append(j)
                except:
                    pass
            new_emp_id = max(int_emp_id_lst) + 1
            last = LastEmpId.objects.first()
            last.emp_id = new_emp_id
            last.save()
            # Creating Leave Balance
            EmployeeLeaveBalance.objects.create(
                emp_id=emp_id, emp_name=emp_name, team=emp_process, pl_balance=0,
                sl_balance=0, present_count=0
            )
            # Creating Attendance
            start_date = datetime.strptime(emp_doj, '%Y-%m-%d').date()
            last_date = date.today() + monthdelta.monthdelta(2)
            last_date = date(last_date.year, last_date.month, 1) - timedelta(days=1)
            delta = last_date - start_date
            date_list = []
            for i in range(delta.days + 1):
                day = start_date + timedelta(days=i)
                date_list.append(day)
            j = Profile.objects.get(emp_id=emp_id)
            for i in date_list:
                try:
                    EcplCalander.objects.get(emp_id=j.emp_id, date=i)
                except EcplCalander.DoesNotExist:
                    EcplCalander.objects.create(date=i, emp_id=j.emp_id, att_actual='Unmarked',
                                                emp_name=j.emp_name, emp_desi=j.emp_desi,
                                                team=j.emp_process, team_id=j.emp_process_id, rm1=j.emp_rm1,
                                                rm2=j.emp_rm2, rm3=j.emp_rm3, rm1_id=j.emp_rm1_id,
                                                rm2_id=j.emp_rm2_id, rm3_id=j.emp_rm3_id)
            date_list_week = []
            start_date = datetime.strptime(emp_doj, '%Y-%m-%d').date()
            if start_date.weekday() != 6:
                for i in range(1, start_date.weekday() + 2):
                    date_list_week.append(start_date - timedelta(days=i))
            for i in date_list_week:
                try:
                    EcplCalander.objects.get(emp_id=j.emp_id, date=i)
                except EcplCalander.DoesNotExist:
                    EcplCalander.objects.create(date=i, emp_id=j.emp_id, att_actual='',
                                                emp_name=j.emp_name, emp_desi=j.emp_desi,
                                                team=j.emp_process, team_id=j.emp_process_id, rm1=j.emp_rm1,
                                                rm2=j.emp_rm2, rm3=j.emp_rm3, rm1_id=j.emp_rm1_id,
                                                rm2_id=j.emp_rm2_id, rm3_id=j.emp_rm3_id)
            date_list_month = []
            start_date = datetime.strptime(emp_doj, '%Y-%m-%d').date()
            start_date = date(start_date.year, start_date.month, 1)
            while start_date < datetime.strptime(emp_doj, '%Y-%m-%d').date():
                date_list_month.append(start_date)
                start_date += timedelta(days=1)
            for i in date_list_month:
                try:
                    EcplCalander.objects.get(emp_id=j.emp_id, date=i)
                except EcplCalander.DoesNotExist:
                    EcplCalander.objects.create(date=i, emp_id=j.emp_id, att_actual='',
                                                emp_name=j.emp_name, emp_desi=j.emp_desi,
                                                team=j.emp_process, team_id=j.emp_process_id, rm1=j.emp_rm1,
                                                rm2=j.emp_rm2, rm3=j.emp_rm3, rm1_id=j.emp_rm1_id,
                                                rm2_id=j.emp_rm2_id, rm3_id=j.emp_rm3_id)

        messages.info(request, 'User and Profile Successfully Created')
        return redirect('/ams/add-new-user')
    else:
        emp_id = request.user.profile.emp_id
        lst_emp_id = LastEmpId.objects.first().emp_id
        emp = Profile.objects.get(emp_id=emp_id)
        all_desi = Designation.objects.all()

        rms = Profile.objects.filter(Q(emp_desi__in=rm_list) | Q(emp_desi__in=management_list)).order_by('emp_name')
        rm3 = Profile.objects.filter(Q(emp_desi__in=manager_list) | Q(emp_desi__in=management_list)).order_by(
            'emp_name')
        all_team = Campaigns.objects.all()

        onboarding = OnboardingnewHRC.objects.filter(user_created=False)
        data = {'emp': emp, 'all_data': all_desi, 'rms': rms, 'rm3': rm3, 'all_team': all_team,
                'onboarding': onboarding,
                "last_emp_id": lst_emp_id, 'hr_om_list': hr_om_list, 'hr_tl_am_list': hr_tl_am_list}
        return render(request, 'ams/hr_add_user.html', data)


@login_required
def addNewDesi(request):
    if request.method == 'POST':
        name = request.POST['new_desg']
        try:
            Designation.objects.get(name__iexact=name)
            messages.success(request, "Designation with same name already present!")
            return redirect('/ams/add-new-user')
        except Designation.DoesNotExist:
            Designation.objects.create(name=name, created_by=request.user.profile.emp_name)
            messages.success(request, "New Designation Added!")
            return redirect('/ams/add-new-user')
    else:
        messages.error(request, "Invalid request! you have been logged out")
        return redirect('/ams/')


@login_required
def viewUsersHR(request):  # Test1
    emp_id = request.user.profile.emp_id
    emp = Profile.objects.get(emp_id=emp_id)
    add = Profile.objects.all()
    data = {'add': add, 'emp': emp}
    return render(request, 'ams/view_user_hr.html', data)


@login_required
def viewEmployeeProfile(request, id, on_id):  # Test 1

    if request.method == 'POST':
        changed_name = request.POST.get('emp_name')
        changed_desi = request.POST.get('emp_desi')
        type = request.POST['from']
        if type == 'name':
            n = Profile.objects.get(id=id)
            n.emp_name = changed_name
            n.save()
            x = Profile.objects.filter(Q(emp_rm1_id=n.emp_id) | Q(emp_rm2_id=n.emp_id) | Q(emp_rm3_id=n.emp_id))
            change = []
            for i in x:
                if i.emp_rm1_id == n.emp_id:
                    i.emp_rm1 = changed_name
                if i.emp_rm2_id == n.emp_id:
                    i.emp_rm2 = changed_name
                if i.emp_rm3_id == n.emp_id:
                    i.emp_rm3 = changed_name
                change.append(i)
            Profile.objects.bulk_update(change, ['emp_rm1', 'emp_rm2', 'emp_rm3'])
            messages.success(request, 'Employee Name Changed Successfully!')
            return redirect('/ams/view-employee-profile/' + str(id) + '/' + str(on_id))
        elif type == 'desi':
            n = Profile.objects.get(id=id)
            n.emp_desi = changed_desi
            n.save()
            messages.success(request, 'Employee Designation Changed Successfully!')
            return redirect('/ams/view-employee-profile/' + str(id) + '/' + str(on_id))

    emp_id = request.user.profile.emp_id
    emp = Profile.objects.get(emp_id=emp_id)
    profile = Profile.objects.get(id=id)
    if on_id == "None":
        onboarding = ""
    else:
        onboarding = OnboardingnewHRC.objects.get(id=int(on_id))
    designations = Designation.objects.all()
    data = {'profile': profile, 'onboard': onboarding, 'emp': emp, "on": on_id, "hr_list": hr_list,
            'hr_om_list': hr_om_list, 'hr_tl_am_list': hr_tl_am_list, 'designations': designations}
    return render(request, 'ams/emp_profile_view.html', data)


@login_required
def teamAttendance(request):  # Team Attendance Page # Test1
    today = date.today()
    yesterday = today - timedelta(days=1)
    dby_date = yesterday - timedelta(days=1)
    user_empid = request.user.profile.emp_id
    emp_list = []
    emps = Profile.objects.filter(Q(emp_rm1_id=user_empid) | Q(emp_rm2_id=user_empid) | Q(emp_rm3_id=user_empid),
                                  Q(agent_status='Active'))
    for i in emps:
        emp_list.append(i.emp_id)
    # Today 
    todays_list_list = EcplCalander.objects.filter(Q(date=today), Q(att_actual='Unmarked'), Q(emp_id__in=emp_list))
    todays_dict_list = []
    for i in todays_list_list:
        todays_dict = {}
        todays_dict['date'] = str(i.date)
        todays_dict['emp_name'] = i.emp_name
        todays_dict['emp_id'] = i.emp_id
        todays_dict['att_actual'] = i.att_actual
        todays_dict_list.append(todays_dict)
    # Yesterday
    ystday_list_list = EcplCalander.objects.filter(Q(date=yesterday), Q(att_actual='Unmarked'), Q(emp_id__in=emp_list))
    ystday_dict_list = []
    for i in ystday_list_list:
        ystday_dict = {}
        ystday_dict['date'] = str(i.date)
        ystday_dict['emp_name'] = i.emp_name
        ystday_dict['emp_id'] = i.emp_id
        ystday_dict['att_actual'] = i.att_actual
        ystday_dict_list.append(ystday_dict)
    # Day Before Yesterday
    dby_list_list = EcplCalander.objects.filter(Q(date=dby_date), Q(att_actual='Unmarked'), Q(emp_id__in=emp_list))
    dby_dict_list = []
    for i in dby_list_list:
        dby_dict = {}
        dby_dict['date'] = str(i.date)
        dby_dict['emp_name'] = i.emp_name
        dby_dict['emp_id'] = i.emp_id
        dby_dict['att_actual'] = i.att_actual
        dby_dict_list.append(dby_dict)
    emp = Profile.objects.get(emp_id=user_empid)
    data = {'todays_att': todays_dict_list, 'ystdays_att': ystday_dict_list, 'dbys_att': dby_dict_list, 'emp': emp,
            'today': calendar.day_name[today.weekday()], 'yesterday': calendar.day_name[yesterday.weekday()],
            'dby_date': calendar.day_name[dby_date.weekday()]}
    return render(request, 'ams/team_attendance.html', data)


@login_required
def applyAttendace(request):  # Test1
    if request.method == 'POST':
        ddate = request.POST['date']
        att_actual = request.POST['att_actual']
        emp_id = request.POST['emp_id']
        now = datetime.now()
        prof = Profile.objects.get(emp_id=emp_id)
        rm1 = prof.emp_rm1
        rm2 = prof.emp_rm2
        rm3 = prof.emp_rm3
        rm1_id = prof.emp_rm1_id
        rm2_id = prof.emp_rm2_id
        rm3_id = prof.emp_rm3_id
        desi = prof.emp_desi
        team = prof.emp_process
        team_id = prof.emp_process_id
        try:
            cal = EcplCalander.objects.get(Q(date=ddate), Q(emp_id=emp_id), ~Q(att_actual='Unmarked'))
            messages.info(request, '*** Already Marked in Calendar, Please Refresh the page and try again ***')
            return redirect('/ams/team-attendance')
        except EcplCalander.DoesNotExist:
            cal = EcplCalander.objects.get(emp_id=emp_id, date=ddate)
            cal.att_actual = att_actual
            cal.approved_on = now
            cal.appoved_by = request.user.profile.emp_name
            cal.rm1 = rm1
            cal.rm2 = rm2
            cal.rm3 = rm3
            cal.rm1_id = rm1_id
            cal.rm2_id = rm2_id
            cal.rm3_id = rm3_id
            cal.emp_desi = desi
            cal.team = team
            cal.team_id = team_id
            cal.save()
        if att_actual == 'Attrition' or att_actual == 'Bench':
            usr = Profile.objects.get(emp_id=emp_id)
            usr.agent_status = att_actual
            usr.save()
            cal = []
            for i in EcplCalander.objects.filter(emp_id=emp_id, date__gt=ddate).exclude(
                    att_actual__in=['PL', 'SL', 'ML']):
                i.att_actual = att_actual
                cal.append(i)
            EcplCalander.objects.bulk_update(cal, ['att_actual'])
        if att_actual == 'NCNS':
            today = date.today()
            yesterday = today - timedelta(days=1)
            dby_date = yesterday - timedelta(days=1)
            date_range = [dby_date, today]
            ncns_count = EcplCalander.objects.filter(emp_id=emp_id, date__range=date_range, att_actual='NCNS').count()
            if ncns_count >= 3:
                usr = Profile.objects.get(emp_id=emp_id)
                usr.agent_status = att_actual
                usr.save()
                cal = []
                for i in EcplCalander.objects.filter(emp_id=emp_id, date__gt=ddate).exclude(
                        att_actual__in=['PL', 'SL', 'ML']):
                    i.att_actual = att_actual
                    cal.append(i)
                EcplCalander.objects.bulk_update(cal, ['att_actual'])

        return redirect('/ams/team-attendance')
    else:
        return HttpResponse('<h1>*** Page not available ***</h1>')


@login_required
def newSingleAttandance(request):  # Test1
    if request.method == 'POST':
        ddate = request.POST['date']
        att_actual = request.POST['att_actual']
        emp_id = request.POST['emp_id']
        now = datetime.now()
        prof = Profile.objects.get(emp_id=emp_id, agent_status='Active')
        rm1 = prof.emp_rm1
        rm2 = prof.emp_rm2
        rm3 = prof.emp_rm3
        rm1_id = prof.emp_rm1_id
        rm2_id = prof.emp_rm2_id
        rm3_id = prof.emp_rm3_id
        desi = prof.emp_desi
        team = prof.emp_process
        team_id = prof.emp_process_id
        try:
            cal = EcplCalander.objects.get(Q(date=ddate), Q(emp_id=emp_id), ~Q(att_actual='Unmarked'))
            messages.info(request, '*** Already Marked in Calendar, Please Refresh the page and try again ***')
            return redirect('/ams/ams-update-attendance')
        except EcplCalander.DoesNotExist:
            cal = EcplCalander.objects.get(emp_id=emp_id, date=ddate)
            cal.att_actual = att_actual
            cal.approved_on = now
            cal.appoved_by = request.user.profile.emp_name
            cal.rm1 = rm1
            cal.rm2 = rm2
            cal.rm3 = rm3
            cal.rm1_id = rm1_id
            cal.rm2_id = rm2_id
            cal.rm3_id = rm3_id
            cal.emp_desi = desi
            cal.team = team
            cal.team_id = team_id
            cal.save()
        if att_actual == 'Attrition' or att_actual == 'Bench':
            usr = Profile.objects.get(emp_id=emp_id)
            usr.agent_status = att_actual
            usr.save()
        if att_actual == 'NCNS':
            today = date.today()
            yesterday = today - timedelta(days=1)
            dby_date = yesterday - timedelta(days=1)
            date_range = [dby_date, today]
            ncns_count = EcplCalander.objects.filter(emp_id=emp_id, date__range=date_range, att_actual='NCNS').count()
            if ncns_count >= 3:
                usr = Profile.objects.get(emp_id=emp_id)
                usr.agent_status = att_actual
                usr.save()
        return redirect('/ams/ams-update-attendance')
    else:
        today = date.today()
        yesterday = today - timedelta(days=1)
        dby_date = yesterday - timedelta(days=1)
        emp_id = request.user.profile.emp_id
        # Today
        todays_list_list = EcplCalander.objects.filter(Q(date=today), Q(emp_id=emp_id), Q(att_actual='Unmarked'))
        # Yesterday
        ystday_list_list = EcplCalander.objects.filter(Q(date=yesterday), Q(emp_id=emp_id), Q(att_actual='Unmarked'))
        # Day before yesterday
        dby_list_list = EcplCalander.objects.filter(Q(date=dby_date), Q(emp_id=emp_id), Q(att_actual='Unmarked'))
        emp = Profile.objects.get(emp_id=emp_id)
        data = {'todays_att': todays_list_list, 'ystdays_att': ystday_list_list, 'dbys_att': dby_list_list, 'emp': emp}
        return render(request, 'ams/attendance.html', data)


@login_required
def viewTeamAttendance(request):  # Test1
    if request.method == 'POST':
        rm = request.user.profile.emp_id
        start_date = request.POST['start_date']
        end_date = request.POST['end_date']
        emp_id = request.POST['emp_id']
        if emp_id == 'All':
            if request.user.profile.emp_desi in management_list:
                all_emp = Profile.objects.filter(Q(emp_rm1_id=rm) | Q(emp_rm2_id=rm) | Q(emp_rm3_id=rm))
                emp_id_lst = [rm]
                for i in all_emp:
                    if i.emp_id not in emp_id_lst:
                        emp_id_lst.append(i.emp_id)
                        under = Profile.objects.filter(
                            Q(emp_rm1_id=i.emp_id) | Q(emp_rm2_id=i.emp_id) | Q(emp_rm3_id=i.emp_id))
                        for j in under:
                            if j.emp_id not in emp_id_lst:
                                emp_id_lst.append(j.emp_id)
                # cal = EcplCalander.objects.filter(emp_id__in=emp_id_lst,
                #        date__range=[start_date, end_date])
                # Export
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="attendance_report.csv"'
                writer = csv.writer(response)
                writer.writerow(
                    ['Date', 'Emp ID', 'Emp Name', 'Attendance', 'Designation', 'RM 1', 'RM 2', 'RM 3', 'Team'])
                calanders = EcplCalander.objects.filter(emp_id__in=emp_id_lst,
                                                        date__range=[start_date, end_date]).values_list(
                    'date', 'emp_id', 'emp_name', 'att_actual', 'emp_desi', 'rm1', 'rm2', 'rm3', 'team')
                for c in calanders:
                    writer.writerow(c)
                return response
            else:
                # cal = EcplCalander.objects.filter(Q(rm1_id=rm) | Q(rm2_id=rm) | Q(rm3_id=rm),
                #                              date__range=[start_date, end_date])
                # Export
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="attendance_report.csv"'
                writer = csv.writer(response)
                writer.writerow(
                    ['Date', 'Emp ID', 'Emp Name', 'Attendance', 'Designation', 'RM 1', 'RM 2', 'RM 3', 'Team'])
                calanders = EcplCalander.objects.filter(Q(emp_id=rm) | Q(rm1_id=rm) | Q(rm2_id=rm) | Q(rm3_id=rm),
                                                        date__range=[start_date, end_date]).values_list(
                    'date', 'emp_id', 'emp_name', 'att_actual', 'emp_desi', 'rm1', 'rm2', 'rm3', 'team')
                for c in calanders:
                    writer.writerow(c)
                return response

        else:
            cal = EcplCalander.objects.filter(date__range=[start_date, end_date], emp_id=emp_id)
        if emp_id == 'self':
            cal = EcplCalander.objects.filter(emp_id=rm,
                                              date__range=[start_date, end_date])
        emp = Profile.objects.get(emp_id=rm)
        data = {'agt_cal_list': cal, 'emp': emp}
        return render(request, 'ams/agent-calander-status.html', data)
    else:
        messages.info(request, "Invalid Request!")
        return redirect('/ams/dashboard-redirect')


@login_required
def weekAttendanceReport(request):  # Test1
    def Merge(a, b, c, d, e, f, g):
        res = {**a, **b, **c, **d, **e, **f, **g}
        return res

    empobj = Profile.objects.get(emp_id=request.user.profile.emp_id)
    emp_id = request.user.profile.emp_id
    day = date.today()
    start = day - timedelta(days=day.weekday())
    start = start + timedelta(days=-1)
    start_year = start.year
    start_month = start.month
    start_day = start.day
    end = start + timedelta(days=6)
    start = date(start_year, start_month, start_day)
    end_year = end.year
    end_month = end.month
    end_day = end.day
    end = date(end_year, end_month, end_day)
    weeks = ['sund', 'mon', 'tue', 'wed', 'thur', 'fri', 'sat']
    emp_id_list = []
    ems = Profile.objects.filter(
        Q(emp_rm1_id=emp_id) | Q(emp_rm2_id=emp_id) | Q(emp_rm3_id=emp_id), Q(agent_status='Active')
    )
    for i in ems:
        if i.emp_id not in emp_id_list:
            emp_id_list.append(i.emp_id)
    weekdays = []
    delta = timedelta(days=1)
    while start <= end:
        weekdays.append(start)
        start += delta
    lst = []  # main data
    calobj = EcplCalander.objects.filter(emp_id__in=emp_id_list, date__in=weekdays)
    for i in calobj:
        samp = {}
        samp['name'] = i.emp_name
        samp["emp_id"] = i.emp_id
        samp[i.date] = i.att_actual
        lst.append(samp)
    n = 0
    new_lst = []
    sort = sorted(lst, key=lambda x: x['emp_id'])

    for i in range(0, len(emp_id_list)):
        individual = Merge(sort[n], sort[n + 1], sort[n + 2], sort[n + 3], sort[n + 4], sort[n + 5], sort[n + 6])
        j = 0
        for w in weekdays:
            a = weeks[j]
            individual[a] = individual[w]
            del individual[w]
            j += 1
        new_lst.append(individual)
        n += 7

    data = {"cal": new_lst, 'emp': empobj}
    return render(request, 'ams/week_attendace_report.html', data)


import csv


@login_required
def attendanceCalendar(request):
    emp_id = request.user.profile.emp_id
    # Month view
    year = date.today().year
    month = date.today().month
    a, num_days = calendar.monthrange(year, month)
    start_date = date(year, month, 1) - monthdelta.monthdelta(1)
    end_date = date(year, month, num_days)
    cal = EcplCalander.objects.filter(Q(date__lte=end_date), Q(emp_id=emp_id))
    month_cal = []
    for i in cal:
        dict = {}
        dict['dt'] = str(i.date)
        dict['st'] = i.att_actual
        month_cal.append(dict)
    data = {'month_cal': month_cal}
    return render(request, 'ams/attendance-calendar.html', data)


@login_required
def teamAttendanceReport(request):  # Test 1
    if request.method == 'POST':
        start_date = request.POST['start_date']
        end_date = request.POST['end_date']
        team_name = request.POST['team_name']
        start_date = start_date
        end_date = end_date
        emp_id = request.user.profile.emp_id
        emp = Profile.objects.get(emp_id=emp_id)
        if team_name == 'All Team':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="attendance_report.csv"'
            writer = csv.writer(response)
            writer.writerow(['Date', 'Emp ID', 'Emp Name', 'Attendance', 'Designation', 'RM 1', 'RM 2', 'RM 3', 'Team'])
            calanders = EcplCalander.objects.filter(date__range=[start_date, end_date]).values_list(
                'date', 'emp_id', 'emp_name', 'att_actual', 'emp_desi', 'rm1', 'rm2', 'rm3', 'team')
            for c in calanders:
                writer.writerow(c)
            return response
        else:
            team_name = Campaigns.objects.get(id=team_name).name
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="attendance_report.csv"'
            writer = csv.writer(response)
            writer.writerow(['Date', 'Emp ID', 'Emp Name', 'Attendance', 'Designation', 'RM 1', 'RM 2', 'RM 3', 'Team'])
            calanders = EcplCalander.objects.filter(team=team_name, date__range=[start_date, end_date]).values_list(
                'date', 'emp_id', 'emp_name', 'att_actual', 'emp_desi', 'rm1', 'rm2', 'rm3', 'team')
            for c in calanders:
                writer.writerow(c)
            return response
    else:
        return HttpResponse('<h2>*** GET not available ***</h2>')


@login_required
def agentSettings(request):  # Test1
    emp_id = request.user.profile.emp_id
    emp = Profile.objects.get(emp_id=emp_id)
    form = PasswordChangeForm(request.user)
    try:
        onboard = OnboardingnewHRC.objects.get(emp_id=emp_id)
        on = True
    except OnboardingnewHRC.DoesNotExist:
        onboard = ''
        on = False
    data = {'emp': emp, 'form': form, 'onboard': onboard, 'profile': emp, 'on': on}
    return render(request, 'ams/settings.html', data)


@login_required
def rmSettings(request):  # Test1
    emp_id = request.user.profile.emp_id
    emp = Profile.objects.get(emp_id=emp_id)
    form = PasswordChangeForm(request.user)
    try:
        onboard = OnboardingnewHRC.objects.get(emp_id=emp_id)
        on = True
    except OnboardingnewHRC.DoesNotExist:
        onboard = ''
        on = False
    data = {'emp': emp, 'form': form, 'onboard': onboard, 'profile': emp, 'on': on}
    return render(request, 'ams/settings.html', data)

def FAQ(request):
    faqs = FaqHRMS.objects.all()
    try:
        first = FaqHRMS.objects.first().id
    except:
        first = 0
    data = {'faqs': faqs, 'first':first}
    return render(request, 'ams/faqs.html', data)

@login_required
def uploadImageToDB(request):  # Test1
    if request.method == 'POST':
        user_image = request.FILES['user-img']
        id = request.POST['id']
        prof = Profile.objects.get(id=id)
        prof.img = user_image
        prof.save()
        return redirect('/ams/dashboard-redirect')
    else:
        pass


@login_required
def mappingHomePage(request):  # Test1
    emp_id = request.user.profile.emp_id
    emp = Profile.objects.get(emp_id=emp_id)
    employees = Profile.objects.filter(Q(emp_rm1_id=emp_id), Q(agent_status='Active'))
    rms = Profile.objects.filter(Q(emp_desi__in=rm_list) | Q(emp_desi__in=management_list)).order_by('emp_name')
    rm3 = Profile.objects.filter(Q(emp_desi__in=manager_list) | Q(emp_desi__in=management_list)).order_by('emp_name')
    teams = Campaigns.objects.all().order_by('name')
    data = {'emp': emp, 'employees': employees, 'rms': rms, 'teams': teams, "rm3": rm3}
    return render(request, 'ams/mapping_home.html', data)


@login_required
def createMappingTicket(request):  # Test1
    if request.method == "POST":
        usr_name = request.user.profile.emp_name
        usr_id = request.user.profile.emp_id
        dt = datetime.now()
        emp_id = request.POST["emp_id"]
        prof = Profile.objects.get(emp_id=emp_id)
        new_rm1_id = request.POST["new_rm1_id"]
        new_rm2_id = request.POST["new_rm2_id"]
        new_rm3_id = request.POST["new_rm3_id"]
        new_process = request.POST["new_process"]
        created_by = usr_name
        created_date = dt
        effective_date = request.POST["effective_date"]
        e = MappingTickets()
        e.emp_name = prof.emp_name
        e.emp_id = emp_id
        e.emp_desi = prof.emp_desi
        e.emp_rm1 = prof.emp_rm1
        e.emp_rm2 = prof.emp_rm2
        e.emp_rm3 = prof.emp_rm3
        e.emp_rm1_id = prof.emp_rm1_id
        e.emp_rm2_id = prof.emp_rm2_id
        e.emp_rm3_id = prof.emp_rm3_id
        e.new_rm1 = Profile.objects.get(emp_id=new_rm1_id).emp_name
        e.new_rm2 = Profile.objects.get(emp_id=new_rm2_id).emp_name
        e.new_rm3 = Profile.objects.get(emp_id=new_rm3_id).emp_name
        e.new_rm1_id = new_rm1_id
        e.new_rm2_id = new_rm2_id
        e.new_rm3_id = new_rm3_id
        e.emp_process = prof.emp_process
        e.new_process = new_process
        e.created_by = created_by
        e.created_by_id = usr_id
        e.created_date = created_date
        e.effective_date = effective_date
        e.save()
        return redirect('/ams/rm-mapping-index')
    else:
        return redirect('/ams/rm-mapping-index')


@login_required
def viewMappingTicketsHr(request):  # Test1
    usr = request.user.profile.emp_id
    tickets = MappingTickets.objects.filter(status=False, new_rm3_id=usr).order_by('created_date')
    emp = Profile.objects.get(emp_id=usr)
    data = {'tickets': tickets, 'emp': emp}
    return render(request, 'ams/view_mapping_tickets.html', data)


@login_required
def approveMappingTicket(request):  # Test1
    if request.method == 'POST':
        usr_name = request.user.profile.emp_name
        id = request.POST['id']
        action = request.POST['action']
        reason = request.POST.get('reason')
        td = datetime.now()
        ticket = MappingTickets.objects.get(id=id)
        ticket.action = action
        ticket.reason = reason
        ticket.status = True
        ticket.approved_by = usr_name
        ticket.approved_date = td
        ticket.save()
        emp_id = ticket.emp_id
        if action == "Approve":
            prof = Profile.objects.get(emp_id=emp_id)
            prof.emp_rm1 = ticket.new_rm1
            prof.emp_rm2 = ticket.new_rm2
            prof.emp_rm3 = ticket.new_rm3
            prof.emp_rm1_id = ticket.new_rm1_id
            prof.emp_rm2_id = ticket.new_rm2_id
            prof.emp_rm3_id = ticket.new_rm3_id
            prof.emp_process = ticket.new_process
            prof.emp_process_id = Campaigns.objects.get(name=ticket.new_process).id
            prof.save()
            cal = EcplCalander.objects.filter(emp_id=emp_id, date__gte=ticket.effective_date)
            for i in cal:
                i.rm1 = ticket.new_rm1
                i.rm2 = ticket.new_rm2
                i.rm3 = ticket.new_rm3
                i.rm1_id = ticket.new_rm1_id
                i.rm2_id = ticket.new_rm2_id
                i.rm3_id = ticket.new_rm3_id
                i.team = ticket.new_process
                i.team_id = Campaigns.objects.get(name=ticket.new_process).id
                i.save()

        return redirect('/ams/view-mapping-tickets')
    else:
        return redirect('/ams/logout')


@login_required
def viewMappingApplicationStatus(request):  # Test1
    usr = request.user.profile.emp_id
    tickets = MappingTickets.objects.filter(created_by_id=usr).order_by('created_date')
    emp = Profile.objects.get(emp_id=usr)
    data = {'tickets': tickets, 'emp': emp}
    return render(request, 'ams/view_mapping_status.html', data)


@login_required
def addNewTeam(request):  # Test1
    mgrs = Profile.objects.filter(emp_desi__in=manager_list, agent_status='Active')
    if request.method == "POST":
        usr = request.user.profile.emp_name
        om = request.POST["om"]
        campaign = request.POST["campaign"]
        try:
            Campaigns.objects.get(name__iexact=campaign)
            messages.info(request, 'Team ' + campaign + 'Not added as Already Present')
            return redirect('/ams/view-all-teams')
        except Campaigns.DoesNotExist:
            cam = Campaigns.objects.create(name=campaign, om=om, created_by=usr)
            cam.save()
            messages.info(request, 'Team ' + campaign + ' Created Successfully')
            return redirect('/ams/view-all-teams')
    else:
        emp_id = request.user.profile.emp_id
        emp = Profile.objects.get(emp_id=emp_id)
        data = {'mgrs': mgrs, 'emp': emp, 'hr_om_list': hr_om_list, 'hr_tl_am_list': hr_tl_am_list}
        return render(request, "ams/add_team.html", data)


@login_required
def viewTeam(request):  # Test1
    if request.user.profile.emp_desi in hr_list:
        teams = Campaigns.objects.all()
        emp_id = request.user.profile.emp_id
        emp = Profile.objects.get(emp_id=emp_id)
        data = {'teams': teams, 'emp': emp, 'hr_om_list': hr_om_list, 'hr_tl_am_list': hr_tl_am_list}
        return render(request, 'ams/view_team.html', data)
    else:
        messages.info(request, '*** You are not authorised to view this page ***')
        return redirect('ams/logout')


@login_required
def applyLeave(request):  # Test1
    if request.method == 'POST':
        emp_name = request.POST["emp_name"]
        emp_id = request.POST["emp_id"]
        prof = Profile.objects.get(emp_id=emp_id)
        emp_desi = prof.emp_desi
        emp_process = prof.emp_process
        emp_rm1_id = prof.emp_rm1_id
        emp_rm2_id = prof.emp_rm2_id
        emp_rm3_id = prof.emp_rm3_id
        emp_rm1 = prof.emp_rm1
        emp_rm2 = prof.emp_rm2
        emp_rm3 = prof.emp_rm3
        leave_type = request.POST["type"]
        start_date = request.POST["startdate"]
        end_date = request.POST["enddate"]
        no_days = request.POST["leave_days"]
        agent_reason = request.POST["reason"]
        unique_id = request.POST['csrfmiddlewaretoken']

        leaves = LeaveTable.objects.filter(emp_id=emp_id).exclude(Q(status="Rejected") | Q(status="Auto Rejected"))
        leave_dates_list = []
        for i in leaves:
            while i.start_date <= i.end_date:
                leave_dates_list.append(i.start_date)
                i.start_date += timedelta(days=1)
        new_leave_dates = []
        check_start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        check_end_date = date(date.today().year, date.today().month, 1) + monthdelta.monthdelta(1)
        check_end_date = check_end_date - timedelta(days=1)
        if check_start_date < date(date.today().year, date.today().month, 1) or check_start_date > date.today() + monthdelta.monthdelta(1):
            if leave_type == 'SL':
                messages.error(request, "Correct the selected dates. "
                                        "Selected dates must be between " + str(
                    datetime.strptime(str(date(date.today().year, date.today().month, 1)), '%Y-%m-%d').strftime(
                        "%d %B, %Y")) + ' and ' + str(
                    datetime.strptime(str(date.today()), '%Y-%m-%d').strftime("%d %B, %Y")))
            else:
                messages.error(request, "Correct the selected dates. "
                                        "Selected dates must be between " + str(
                    datetime.strptime(str(date.today()), '%Y-%m-%d').strftime(
                        "%d %B, %Y")) + ' and ' + str(
                    datetime.strptime(str(check_end_date), '%Y-%m-%d').strftime("%d %B, %Y")))
            return redirect('/ams/ams-apply_leave')
        if check_start_date < date(date.today().year, date.today().month, 1):
            messages.error(request, "You cannot apply leave for previous months. Please select current month dates.")
            return redirect('/ams/ams-apply_leave')
        list_start_date = datetime.strptime(start_date,
                                            '%Y-%m-%d').date()  # To Convert type of start_date from string to date
        list_end_date = datetime.strptime(end_date,
                                          '%Y-%m-%d').date()  # To Convert type of end_date from string to date
        while list_start_date <= list_end_date:
            new_leave_dates.append(list_start_date)
            list_start_date += timedelta(days=1)

        common_dates = set(leave_dates_list) & set(new_leave_dates)
        if common_dates:
            messages.error(request, "Leaves have already been applied for selected date(s).")
            return redirect('/ams/ams-apply_leave')
        else:
            e = LeaveTable()
            e.unique_id = unique_id
            e.applied_date = datetime.now()
            e.leave_type = leave_type
            e.start_date = start_date
            e.end_date = end_date
            e.no_days = no_days
            e.agent_reason = agent_reason
            e.emp_name = emp_name
            e.emp_id = emp_id
            e.emp_desi = emp_desi
            e.emp_process = emp_process
            e.emp_rm1 = emp_rm1
            e.emp_rm2 = emp_rm2
            e.emp_rm3 = emp_rm3
            e.emp_rm1_id = emp_rm1_id
            e.emp_rm2_id = emp_rm2_id
            e.emp_rm3_id = emp_rm3_id
            rm1_desi = Profile.objects.get(emp_id=emp_rm1_id).emp_desi

            if rm1_desi in manager_list or rm1_desi in hr_om_list:
                e.tl_status = 'Approved'
                e.tl_approval = True
                e.tl_date = datetime.now()
                e.tl_reason = 'OM as TL'
            if emp_desi in manager_list or emp_desi in tl_am_list or emp_desi in hr_tl_am_list or emp_desi in hr_om_list:
                e.tl_status = 'Approved'
                e.tl_date = datetime.now()
                e.tl_approval = True
                e.tl_reason = 'Self Approved'
            e.save()
            leave_balance = EmployeeLeaveBalance.objects.get(emp_id=emp_id)
            if leave_type == 'PL':
                leave_balance.pl_balance -= int(no_days)
                leave_balance.save()
            elif leave_type == 'SL':
                leave_balance.sl_balance -= int(no_days)
                leave_balance.save()

            leave_history = leaveHistory()
            leave_history.leave_type = leave_type
            leave_history.transaction = 'Leave Applied (ID: ' + str(e.id) + ')'
            leave_history.date = date.today()
            leave_history.no_days = int(no_days)
            leave_history.emp_id = emp_id
            pl = EmployeeLeaveBalance.objects.get(emp_id=emp_id).pl_balance
            sl = EmployeeLeaveBalance.objects.get(emp_id=emp_id).sl_balance
            leave_history.total = pl + sl
            leave_history.save()
            return redirect('/ams/ams-apply_leave')
    else:
        emp_id = request.user.profile.emp_id
        emp = Profile.objects.get(emp_id=emp_id)
        leave = LeaveTable.objects.filter(emp_id=emp_id)
        try:
            Profile.objects.get(emp_id=emp_id, doj=None)
            doj = date(2020, 1, 1)
            today = date.today()
            probation = (today - doj).days
        except Profile.DoesNotExist:
            if emp.doj == None:
                doj = date(2020, 1, 1)
            else:
                doj = emp.doj
            today = date.today()
            probation = (today - doj).days
        try:
            leave_balance = EmployeeLeaveBalance.objects.get(emp_id=emp_id)
        except EmployeeLeaveBalance.DoesNotExist:
            leave_balance = {'sl_balance': 0, 'pl_balance': 0}
        leave_his = leaveHistory.objects.filter(emp_id=emp_id).values('date', 'transaction',
                                                                      'leave_type', 'total', 'id').annotate(
            no_days=Sum('no_days'))
        data = {'emp': emp, 'leave': leave, 'leave_balance': leave_balance, 'probation': probation,
                'leave_his': leave_his}
        return render(request, 'ams/apply-leave.html', data)


@login_required
def viewleaveListRM1(request):  # Test1
    emp_id = request.user.profile.emp_id
    emp = Profile.objects.get(emp_id=emp_id)
    leave_request = LeaveTable.objects.filter(emp_rm1_id=emp_id, tl_approval=False)
    data = {'emp': emp, 'leave_request': leave_request}
    return render(request, 'ams/leave_approval_rm1.html', data)


@login_required
def approveLeaveRM1(request):  # Test1
    if request.method == "POST":
        id = request.POST["id"]
        e = LeaveTable.objects.get(id=id)
        emp_id = e.emp_id
        leave_type = e.leave_type
        no_days = e.no_days
        tl_response = request.POST['tl_response']
        tl_reason = request.POST['tl_reason']
        if tl_response == 'Approve':
            if e.start_date < date(date.today().year, date.today().month, 1):
                messages.error(request, 'Previous Month Leaves cannot be approved in this month.')
                return redirect('/ams/view-leave-list')
            else:
                tl_approval = True
                tl_status = 'Approved'
                status = 'Pending'
        else:
            tl_approval = True
            tl_status = 'Rejected'
            status = 'Rejected'
            leave_balance = EmployeeLeaveBalance.objects.get(emp_id=emp_id)
            if leave_type == 'PL':
                leave_balance.pl_balance += int(no_days)
                leave_balance.save()
            elif leave_type == 'SL':
                leave_balance.sl_balance += int(no_days)
                leave_balance.save()
            leave_history = leaveHistory()
            leave_history.leave_type = leave_type
            leave_history.transaction = 'Leave Refund as RM1 Rejected, Leave applied on: ' + str(
                e.applied_date) + ' (ID: ' + str(e.id) + ')'
            leave_history.date = date.today()
            leave_history.no_days = int(no_days)
            leave_history.emp_id = emp_id
            pl = EmployeeLeaveBalance.objects.get(emp_id=emp_id).pl_balance
            sl = EmployeeLeaveBalance.objects.get(emp_id=emp_id).sl_balance
            leave_history.total = pl + sl
            leave_history.save()

        e.tl_approval = tl_approval
        e.tl_reason = tl_reason
        e.tl_status = tl_status
        e.tl_date = datetime.now()
        e.status = status
        e.save()
        return redirect('/ams/view-leave-list')


@login_required
def applyEscalation(request):  # Test1
    if request.method == "POST":
        id = request.POST["id"]
        reason = request.POST['reason']
        e = LeaveTable.objects.get(id=id)
        e.escalation = True
        e.escalation_reason = reason
        e.save()
        emp_id = e.emp_id
        no_days = e.no_days
        type = e.leave_type
        a = EmployeeLeaveBalance.objects.get(emp_id=emp_id)
        if type == "PL":
            a.pl_balance = a.pl_balance - no_days
        else:
            a.sl_balance = a.sl_balance - no_days
        a.save()

        leave_history = leaveHistory()
        leave_history.leave_type = e.leave_type
        leave_history.transaction = 'Applied for Escalation, Leave applied on: ' + str(e.applied_date) + ' (ID: ' + str(
            e.id) + ')'
        leave_history.date = date.today()
        leave_history.no_days = int(no_days)
        leave_history.emp_id = emp_id
        pl = EmployeeLeaveBalance.objects.get(emp_id=emp_id).pl_balance
        sl = EmployeeLeaveBalance.objects.get(emp_id=emp_id).sl_balance
        leave_history.total = pl + sl
        leave_history.save()

        return redirect('/ams/ams-apply_leave')
    else:
        pass


@login_required
def viewEscalation(request):  # Test1
    leave_request = LeaveTable.objects.filter(emp_rm3_id=request.user.profile.emp_id, tl_approval=True, escalation=True,
                                              manager_approval=False)
    data = {'leave_request': leave_request}
    return render(request, 'ams/leave_escalation.html', data)


@login_required
def viewLeaveHistory(request):  # Test1
    emp_id = request.user.profile.emp_id
    leave = Profile.objects.filter(Q(emp_rm1_id=emp_id) | Q(emp_rm2_id=emp_id) | Q(emp_rm3_id=emp_id))
    direct = LeaveTable.objects.filter(Q(emp_rm1_id=emp_id) | Q(emp_rm2_id=emp_id) | Q(emp_rm3_id=emp_id))
    leave_lst = []
    for i in leave:
        under = LeaveTable.objects.filter(Q(emp_rm1_id=i.emp_id) | Q(emp_rm2_id=i.emp_id) | Q(emp_rm3_id=i.emp_id))
        for j in under:
            if j not in leave_lst:
                leave_lst.append(j)
    for i in direct:
        if i not in leave_lst:
            leave_lst.append(i)
    data = {'leave': leave_lst}
    return render(request, 'ams/view_employee_leave_history.html', data)


@login_required
def editAgentStatus(request):  # Test1
    if request.method == 'POST':
        id = request.POST['id']
        agent_status = request.POST['new_status']
        effective = request.POST['effective']
        reason = request.POST['reason']
        profile = Profile.objects.get(id=id)
        current_status = profile.agent_status
        profile.agent_status = agent_status
        profile.save()
        sh = AgentActiveStatusHist.objects.create(emp_id=profile.emp_id, emp_name=profile.emp_name,
                                                  current_status=current_status,
                                                  new_status=agent_status, date=date.today(), reason=reason,
                                                  changed_by=request.user.profile.emp_name)
        sh.save()
        if agent_status == 'Active':
            cal_list = []
            cal = EcplCalander.objects.filter(emp_id=profile.emp_id, date__gte=effective)
            for i in cal:
                if i.att_actual != "PL" or i.att_actual != "SL":
                    i.att_actual = 'Unmarked'
                    cal_list.append(i)
            EcplCalander.objects.bulk_update(cal_list, ['att_actual'])

        if agent_status == 'Attrition':
            cal_list = []
            cal = EcplCalander.objects.filter(emp_id=profile.emp_id, date__gte=effective)
            for i in cal:
                if i.att_actual != "PL" or i.att_actual != "SL":
                    i.att_actual = 'Attrition'
                    cal_list.append(i)
            EcplCalander.objects.bulk_update(cal_list, ['att_actual'])

        if agent_status == 'Bench':
            cal_list = []
            cal = EcplCalander.objects.filter(emp_id=profile.emp_id, date__gte=effective)
            for i in cal:
                if i.att_actual != "PL" or i.att_actual != "SL":
                    i.att_actual = 'Bench'
                    cal_list.append(i)
            EcplCalander.objects.bulk_update(cal_list, ['att_actual'])

        if agent_status == 'NCNS':
            cal_list = []
            cal = EcplCalander.objects.filter(emp_id=profile.emp_id, date__gte=effective)
            for i in cal:
                if i.att_actual != "PL" or i.att_actual != "SL":
                    i.att_actual = 'NCNS'
                    cal_list.append(i)
            EcplCalander.objects.bulk_update(cal_list, ['att_actual'])
        return redirect('/ams/viewusers')
    else:
        return HttpResponse('<h1>Not Get Method</h1>')


@login_required
def attendanceCorrection(request):  # Test1
    emp_idd = request.user.profile.emp_id
    emp = Profile.objects.get(emp_id=emp_idd)
    if request.method == 'POST':
        datee = request.POST['date']
        emp_id = request.POST['emp_id']
        profile = Profile.objects.get(emp_id=emp_id)
        if datetime.strptime(datee, "%Y-%m-%d").month == date.today().month:
            if profile.doj:
                if datetime.strptime(datee, "%Y-%m-%d").date() >= profile.doj:
                    cal = EcplCalander.objects.get(Q(date=datee), Q(emp_id=emp_id))
                    data = {'cal': cal, 'emp': emp}
                    return render(request, 'ams/view_att_correction_apply.html', data)
                else:
                    messages.error(request, "Invalid Date Request as EMP DOJ is: " + str(profile.doj))
                    return redirect('/ams/attendance-correction')
            else:
                messages.error(request, "Invalid EMP DOJ. Contact CC team with the Employee's DOJ.")
                return redirect('/ams/attendance-correction')
        else:
            messages.error(request, "You cannot correct previous month attendance!")
            return redirect('/ams/attendance-correction')


    else:
        all_emp = Profile.objects.filter(Q(agent_status='Active'),
                                         Q(emp_rm1_id=emp_idd) | Q(emp_rm2_id=emp_idd) | Q(emp_rm3_id=emp_idd))
        atthist = AttendanceCorrectionHistory.objects.filter(applied_by_id=emp_idd)
        data = {'all_emp': all_emp, 'emp': emp, 'atthist': atthist}
        return render(request, 'ams/view_att_correction.html', data)


@login_required
def applyCorrection(request):  # Test1
    applied_by = request.user.profile.emp_name
    applied_by_id = request.user.profile.emp_id
    if request.method == 'POST':
        id = request.POST['id']
        att_new = request.POST['att_new']
        att_old = request.POST['att_old']
        date = request.POST['date']
        reason = request.POST['reason']
        emp_id = request.POST['emp_id']
        emp_obj = Profile.objects.get(emp_id=emp_id)
        cal = EcplCalander.objects.get(id=id)
        emp_name = cal.emp_name
        emp_id = cal.emp_id
        atthist = AttendanceCorrectionHistory()
        atthist.applied_by = applied_by
        atthist.applied_by_id = applied_by_id
        atthist.applied_date = datetime.today()
        atthist.date_for = date
        atthist.att_old = att_old
        atthist.att_new = att_new
        atthist.emp_name = emp_name
        atthist.emp_id = emp_id
        atthist.rm3_id = emp_obj.emp_rm3_id
        atthist.rm3_name = emp_obj.emp_rm3
        atthist.om_response = 'Pending by ' + str(emp_obj.emp_rm3) + " (" + str(emp_obj.emp_rm3_id) + ")"
        atthist.cal_id = id
        atthist.reason = reason
        atthist.save()
        messages.info(request, 'Attendance Correction Request has been sent Successfully')
        return redirect('/ams/attendance-correction')
    else:
        pass


@login_required
def approveAttendanceRequest(request):  # test1
    emp_idd = request.user.profile.emp_id
    emp = Profile.objects.get(emp_id=emp_idd)
    if request.method == 'POST':
        id = request.POST['id']
        cal_id = request.POST['cal_id']
        om_resp = request.POST['om_resp']
        comments = request.POST['comments']
        hist = AttendanceCorrectionHistory.objects.get(id=id)
        cal = EcplCalander.objects.get(id=cal_id)
        if om_resp == 'Approved':
            if hist.date_for < date(date.today().year, date.today().month, 1):
                messages.error(request, 'Previous Month Request cannot be approved in this month.')
                return redirect('/ams/approve-att-correction-req')
            else:
                cal.att_actual = hist.att_new
                cal.approved_on = datetime.now()
                cal.appoved_by = emp.emp_name
                cal.unique_id = 'Attendance Correction'
                cal.save()
                att_actual = hist.att_new
                old_att = hist.att_old
                if att_actual == 'Attrition' or att_actual == 'Bench':
                    usr = Profile.objects.get(emp_id=cal.emp_id)
                    usr.agent_status = att_actual
                    usr.save()
                    calendar = []
                    for i in EcplCalander.objects.filter(emp_id=cal.emp_id, date__gt=cal.date).exclude(att_actual__in=['PL', 'SL', 'ML']):
                        i.att_actual = att_actual
                        calendar.append(i)
                    EcplCalander.objects.bulk_update(calendar, ['att_actual'])
                if att_actual == 'NCNS':
                    today = cal.date
                    yesterday = today - timedelta(days=1)
                    dby_date = yesterday - timedelta(days=1)
                    tmr = today + timedelta(days=1)
                    daftmr = tmr + timedelta(days=1)
                    date_range = [dby_date, today]
                    ncns_count = EcplCalander.objects.filter(emp_id=cal.emp_id, date__range=date_range,
                                                             att_actual='NCNS').count()
                    if ncns_count >= 3:
                        usr = Profile.objects.get(emp_id=cal.emp_id)
                        usr.agent_status = att_actual
                        usr.save()
                        calendar = []
                        for i in EcplCalander.objects.filter(emp_id=cal.emp_id, date__gt=cal.date).exclude(att_actual__in=['PL', 'SL', 'ML']):
                            i.att_actual = att_actual
                            calendar.append(i)
                        EcplCalander.objects.bulk_update(calendar, ['att_actual'])
                if old_att == 'PL':
                    leave = EmployeeLeaveBalance.objects.get(emp_id=cal.emp_id)
                    leave.pl_balance += 1
                    leave.save()
                    leaveHistory.objects.create(
                        emp_id=cal.emp_id, date=date.today(), leave_type='PL',
                        transaction='Attendance Correction, Leave Refund which was applied on ' + str(cal.date), no_days=1,
                        total=leave.pl_balance + leave.sl_balance
                    )
                if old_att == 'SL':
                    leave = EmployeeLeaveBalance.objects.get(emp_id=cal.emp_id)
                    leave.sl_balance += 1
                    leave.save()
                    leaveHistory.objects.create(
                        emp_id=cal.emp_id, date=date.today(), leave_type='PL',
                        transaction='Attendance Correction, Leave Refund which was applied on ' + str(cal.date), no_days=1,
                        total=leave.pl_balance + leave.sl_balance
                    )
        # if om_resp == 'Rejected':
        #     if hist.att_new == 'Half Day':
        #         leave_bal = EmployeeLeaveBalance.objects.get(emp_id=cal.emp_id)
        #         leave_bal.pl_balance += 0.5
        #         leave_bal.save()
        #         leaveHistory.objects.create(
        #             emp_id=cal.emp_id, date=date.today(), leave_type='PL',
        #             transaction='Half day got rejected', no_days=0.5,
        #             total=leave_bal.pl_balance + leave_bal.sl_balance
        #         )

        hist.status = True
        hist.comments = comments
        hist.approved_by = request.user.profile.emp_name
        hist.approved_on = datetime.now()
        hist.om_response = om_resp
        hist.save()
        return redirect('/ams/approve-att-correction-req')
    else:
        att_hist = AttendanceCorrectionHistory.objects.filter(status=False, rm3_id=emp_idd)
        data = {'att_hist': att_hist, 'emp': emp}
        return render(request, 'ams/hr_attendance_correction.html', data)


@login_required
def changeEmpPassword(request):
    if request.method == "POST":
        new_pass = request.POST["new_pass"]
        con_pass = request.POST["con_pass"]
        emp_id = request.POST["emp_id"]
        user = User.objects.get(username=emp_id)
        profile = Profile.objects.get(user=user)
        if new_pass == con_pass:
            user.password = make_password(new_pass)
            user.save()
            profile.pc = False
            profile.save()
            messages.info(request, "Password Changed Successfully!!")
            return redirect("/ams/rm-mapping-index")
        else:
            messages.error(request, "New Password and Confirm Password does not match! try again!!")
            return redirect("/ams/rm-mapping-index")
    else:
        messages.error(request, "Unauthorized access you have been Logged Out :)")
        return redirect("/ams/")


@login_required
def SLProofSubmit(request):  # Test1
    if request.method == 'POST':
        id = request.POST['id']
        proof = request.FILES['proof']
        leave = LeaveTable.objects.get(id=id)
        last_date = leave.end_date
        timee = (date.today() - last_date).days
        if timee <= 2:
            leave.proof = proof
            leave.save()
            return redirect('/ams/ams-apply_leave')
        else:
            messages.info(request, "The time has exceeded cannot upload now :)")
            return redirect('/ams/ams-apply_leave')


@login_required
def maternityLeave(request):
    emp_desi = request.user.profile.emp_desi
    if emp_desi in hr_tl_am_list or hr_om_list:
        if request.method == 'POST':
            emp_id = request.POST['emp_id']
            startdate = request.POST['startdate']
            startdate = datetime.strptime(startdate, '%Y-%m-%d').date()
            enddate = startdate + monthdelta.monthdelta(6)
            datelist = []
            ecplcalupdate = []
            ecplcalcreate = []
            emp = Profile.objects.get(emp_id=emp_id)
            while startdate < enddate:
                datelist.append(startdate)
                startdate += timedelta(days=1)
            for i in datelist:
                try:
                    cal = EcplCalander.objects.get(emp_id=emp_id, date=i)
                    cal.att_actual = 'ML'
                    cal.appoved_by = request.user.profile.emp_name
                    cal.approved_on = datetime.now()
                    ecplcalupdate.append(cal)
                except:
                    employees = EcplCalander()
                    employees.date = i
                    employees.emp_id = emp.emp_id
                    employees.att_actual = 'ML'
                    employees.emp_name = emp.emp_name
                    employees.emp_desi = emp.emp_desi
                    employees.team = emp.emp_process
                    employees.team_id = emp.emp_process_id
                    employees.rm1 = emp.emp_rm1
                    employees.rm2 = emp.emp_rm2
                    employees.rm3 = emp.emp_rm3
                    employees.rm1_id = emp.emp_rm1_id
                    employees.rm2_id = emp.emp_rm2_id
                    employees.rm3_id = emp.emp_rm3_id
                    ecplcalcreate.append(employees)
            EcplCalander.objects.bulk_update(ecplcalupdate, ['att_actual', 'appoved_by', 'approved_on'])
            EcplCalander.objects.bulk_create(ecplcalcreate)
            messages.success(
                request, 'ML has been marked successfully for ' + str(emp.emp_name) +
                         ' (' + str(emp.emp_id) + '). And the next reporting date will be ' + str(enddate))
            return redirect('/ams/maternity-leave')
        else:
            profiles = Profile.objects.all()
            data = {'profiles': profiles}
            return render(request, 'ams/maternity-leave.html', data)
    else:
        messages.error(request, 'Invalid Request you have been logged out!')
        return redirect('/ams/')


@login_required
def onboardingBulkUpload(request):
    if request.method == 'POST':
        dataset = Dataset()
        person_resource = OnboardingnewHRCResourse()
        new_persons = request.FILES['myfile']
        imported_data = dataset.load(new_persons.read().decode('utf-8'), format='csv', headers=True)
        result = person_resource.import_data(imported_data, dry_run=True)  # Test the data import
        if not result.has_errors():
            person_resource.import_data(imported_data, dry_run=False)
            messages.success(request, "Successfully Uploaded :)")
        else:
            messages.success(request,
                             "Something went wrong. Please Correct the Data and make sure all fields are filled.")
        profile_list = []
        onboarding = []
        for i in OnboardingnewHRC.objects.filter(user_created=False):
            profile = Profile.objects.get(emp_id=i.emp_id)
            profile.on_id = i.id
            profile_list.append(profile)
            i.user_created = True
            onboarding.append(i)

        Profile.objects.bulk_update(profile_list, ['on_id'])
        OnboardingnewHRC.objects.bulk_update(onboarding, ['user_created'])

        return redirect('/ams/bulk-onboarding')
    else:
        return render(request, 'ams/bulk_onboarding.html')


@login_required
def AttendanceReportAdmin(request):
    emp_id = request.user.profile.emp_id
    emp_desi = request.user.profile.emp_desi
    if emp_id in admin_list or emp_desi in hr_list:
        if request.method == 'POST':
            emp_id = request.POST['emp_id']
            start = request.POST['start']
            end = request.POST['end']
            calendar = EcplCalander.objects.filter(emp_id=emp_id, date__range=[start, end])

            profiles = Profile.objects.all()
            data = {'profiles': profiles, 'calendar': calendar}
            return render(request, 'ams/admin_main/attendance-report.html', data)
        else:
            profiles = Profile.objects.all()
            data = {'profiles': profiles}
            return render(request, 'ams/admin_main/attendance-report.html', data)
    else:
        messages.info(request, 'Unauthorized Access')
        return redirect('/ams/dashboard-redirect')


@login_required
def AttendanceCorrectionAdmin(request):
    emp_id = request.user.profile.emp_id
    if emp_id in admin_list:
        if request.method == 'POST':
            type = request.POST['type']
            if type == 'single':
                emp_id = request.POST['emp_id']
                start = request.POST['start']
                try:
                    calendar = EcplCalander.objects.get(emp_id=emp_id, date=start)
                    profiles = Profile.objects.all()
                    data = {'profiles': profiles, 'cal': calendar}
                    return render(request, 'ams/admin_main/attendance-correction.html', data)
                except:
                    messages.error(request, 'No attendance for selected employee on selected date')
                    return redirect('/ams/admin-attendance-correction')
            if type == 'bulk':
                emp_id = request.POST.getlist('emp_id')
                start = request.POST['start']
                end = request.POST['end']
                calendar = EcplCalander.objects.filter(emp_id__in=emp_id, date__range=[start, end])
                if calendar.exists():
                    calendar = calendar
                else:
                    calendar = {'val': True}
                profiles = Profile.objects.all()
                data = {'profiles': profiles, 'bulk_cal': calendar, 'emp_id': emp_id, 'start': start, 'end': end}
                return render(request, 'ams/admin_main/attendance-correction.html', data)
        else:
            profiles = Profile.objects.all()
            data = {'profiles': profiles}
            return render(request, 'ams/admin_main/attendance-correction.html', data)
    else:
        messages.info(request, 'Unauthorized Access')
        return redirect('/ams/dashboard-redirect')


@login_required
def AttendanceCorrectionSubmitAdmin(request):
    emp_id = request.user.profile.emp_id
    emp_name = request.user.profile.emp_name
    if emp_id in admin_list:
        if request.method == 'POST':
            type = request.POST['type']
            cal_update = []
            cal_create = []
            att_create = []
            if type == 'single':
                id = request.POST['id']
                new_att = request.POST['new_att']
                cal = EcplCalander.objects.get(id=id)
                old_att = cal.att_actual
                cal.att_actual = new_att
                cal.approved_on = datetime.now()
                cal.appoved_by = "CC Team"
                cal_update.append(cal)
                att_his = AttendanceCorrectionHistory(
                    applied_by=emp_name, applied_by_id=emp_id, applied_date=date.today(),
                    date_for=cal.date, att_old=old_att, att_new=new_att,
                    emp_name=cal.emp_name, emp_id=cal.emp_id, rm3_name=cal.rm3,
                    rm3_id=cal.rm3_id, approved_by='CC TEAM', status=True, cal_id=cal.id,
                    om_response="Approved", comments="Approved by CCTeam", reason="Approved by CCTeam"
                )
                att_create.append(att_his)
            elif type == 'bulk':
                emp_id = request.POST.get('emp_id')
                emp_id = ast.literal_eval(emp_id)
                start = request.POST['start']
                start = datetime.strptime(start, '%Y-%m-%d').date()
                end = request.POST['end']
                end = datetime.strptime(end, '%Y-%m-%d').date()
                new_att = request.POST['new_att']
                date_list = []
                while start <= end:
                    date_list.append(start)
                    start += timedelta(days=1)
                for i in date_list:
                    for j in emp_id:
                        emp = Profile.objects.get(emp_id=j)
                        try:
                            cal = EcplCalander.objects.get(emp_id=j, date=i)
                            old_att = cal.att_actual
                            cal.att_actual = new_att
                            if new_att == 'Unmarked':
                                cal.approved_on = None
                                cal.appoved_by = None
                            else:
                                cal.approved_on = datetime.now()
                                cal.appoved_by = "CC Team"
                            cal_update.append(cal)
                            att_his = AttendanceCorrectionHistory(
                                applied_by=emp_name, applied_by_id=request.user.profile.emp_id, applied_date=date.today(),
                                date_for=cal.date, att_old=old_att, att_new=new_att,
                                emp_name=emp.emp_name, emp_id=emp.emp_id, rm3_name=emp.emp_rm3,
                                rm3_id=emp.emp_rm3_id, approved_by='CC TEAM', status=True, cal_id=cal.id,
                                om_response="Approved", comments="Approved by CCTeam", reason="Approved by CCTeam"
                            )
                            att_create.append(att_his)
                        except EcplCalander.DoesNotExist:
                            if new_att == 'Unmarked':
                                cal = EcplCalander(
                                    emp_id=j, date=i, team=emp.emp_process, emp_name=emp.emp_name,
                                    emp_desi=emp.emp_desi, att_actual=new_att,
                                    rm1=emp.emp_rm1, rm2=emp.emp_rm2, rm3=emp.emp_rm3,
                                    rm1_id=emp.emp_rm1_id, rm2_id=emp.emp_rm2_id, rm3_id=emp.emp_rm3_id,
                                    team_id=emp.emp_process_id
                                )
                                cal.save()
                            else:
                                cal = EcplCalander(
                                    emp_id=j, date=i, team=emp.emp_process, emp_name=emp.emp_name,
                                    emp_desi=emp.emp_desi, att_actual=new_att, approved_on=datetime.now(),
                                    appoved_by='CC Team', rm1=emp.emp_rm1, rm2=emp.emp_rm2, rm3=emp.emp_rm3,
                                    rm1_id=emp.emp_rm1_id, rm2_id=emp.emp_rm2_id, rm3_id=emp.emp_rm3_id,
                                    team_id=emp.emp_process_id
                                )
                                cal.save()
                            att_his = AttendanceCorrectionHistory(
                                applied_by=emp_name, applied_by_id=request.user.profile.emp_id, applied_date=date.today(),
                                date_for=cal.date, att_old=None, att_new=new_att,
                                emp_name=emp.emp_name, emp_id=emp.emp_id, rm3_name=emp.emp_rm3,
                                rm3_id=emp.emp_rm3_id, approved_by='CC TEAM', status=True, cal_id=cal.id,
                                om_response="Approved", comments="Approved by CCTeam", reason="Approved by CCTeam"
                            )
                            att_create.append(att_his)
            EcplCalander.objects.bulk_create(cal_create)
            EcplCalander.objects.bulk_update(cal_update, ['att_actual', 'approved_on', 'appoved_by'])
            AttendanceCorrectionHistory.objects.bulk_create(att_create)
            messages.info(request, 'Successfully Changed!')
            return redirect('/ams/admin-attendance-correction')
        else:
            messages.info(request, 'Unauthorized Access')
            return redirect('/ams/dashboard-redirect')
    else:
        messages.info(request, 'Unauthorized Access')
        return redirect('/ams/dashboard-redirect')


@login_required
def getMapping(request):
    emp_id = request.user.profile.emp_id
    if emp_id in admin_list:
        if request.method == "POST":
            id = request.POST["id"]
            profiles = Profile.objects.all()
            profile = Profile.objects.get(id=id)
            departments = Campaigns.objects.all()
            desi = Designation.objects.all()
            rms = Profile.objects.filter(
                Q(emp_desi__in=hr_list) | Q(emp_desi__in=management_list) | Q(emp_desi__in=manager_list) | Q(
                    emp_desi__in=tl_am_list), Q(agent_status='Active')
            )
            data = {'profile': profile, 'profiles': profiles, 'departments': departments, 'desi': desi, 'rms': rms}
            return render(request, 'ams/admin_main/mapping-correction.html', data)
        else:
            profiles = Profile.objects.all()
            data = {'profiles': profiles}
            return render(request, 'ams/admin_main/mapping-correction.html', data)
    else:
        messages.info(request, 'Unauthorized Access')
        return redirect('/ams/dashboard-redirect')


@login_required
def AdminLists(request):
    emp_id = request.user.profile.emp_id
    if emp_id in admin_list:
        if request.method == "POST":
            list = request.POST["list"]
            mylist = ''
            if list == 'ta':
                mylist = ta_list
            elif list == 'tl-am':
                mylist = tl_am_list
            elif list == 'manager':
                mylist = manager_list
            elif list == 'management':
                mylist = management_list
            elif list == 'hr':
                mylist = hr_list
            elif list == 'agent':
                mylist = agent_list
            elif list == 'rm':
                mylist = rm_list
            elif list == 'hr-tl':
                mylist = hr_tl_am_list
            elif list == 'hr-om':
                mylist = hr_om_list
            elif list == 'admin':
                mylist = admin_list
            elif list == 'administration':
                mylist = administration_list
            data = {'mylist': mylist, 'list': list}
            return render(request, 'ams/admin_main/lists.html', data)
        else:
            return render(request, 'ams/admin_main/lists.html')
    else:
        messages.info(request, 'Unauthorized Access')
        return redirect('/ams/dashboard-redirect')

@login_required
def RemoveFromList(request):
    emp_id = request.user.profile.emp_id
    if emp_id in admin_list:
        if request.method == "POST":
            list = request.POST["list"]
            item = request.POST["item"]
            if list == 'ta':
                ta_list.remove(item)
            elif list == 'tl-am':
                tl_am_list.remove(item)
            elif list == 'manager':
                manager_list.remove(item)
            elif list == 'management':
                management_list.remove(item)
            elif list == 'hr':
                hr_list.remove(item)
            elif list == 'agent':
                agent_list.remove(item)
            elif list == 'rm':
                rm_list.remove(item)
            elif list == 'hr-tl':
                hr_tl_am_list.remove(item)
            elif list == 'hr-om':
                hr_om_list.remove(item)
            elif list == 'admin':
                admin_list.remove(item)
            elif list == 'administration':
                administration_list.remove(item)
            messages.info(request, 'Successfully Removed '+str(item))
            return redirect('/ams/lists')
        else:
            messages.info(request, 'Unauthorized Access')
            return redirect('/ams/dashboard-redirect')
    else:
        messages.info(request, 'Unauthorized Access')
        return redirect('/ams/dashboard-redirect')


@login_required
def changeMapping(request):
    if request.method == "POST":
        id = request.POST["id"]
        rm1 = request.POST["rm1"]
        rm1 = Profile.objects.get(id=rm1)
        rm2 = request.POST["rm2"]
        rm2 = Profile.objects.get(id=rm2)
        rm3 = request.POST["rm3"]
        rm3 = Profile.objects.get(id=rm3)
        campaign_id = request.POST["emp_department"]
        cam = Campaigns.objects.get(id=campaign_id)
        desig_id = request.POST["emp_desi"]
        desi = Designation.objects.get(id=desig_id)
        e = Profile.objects.get(id=id)
        if e.emp_rm1_id != rm1.emp_id or e.emp_rm2_id != rm2.emp_id or e.emp_rm3_id != rm3.emp_id:
            MappingTickets.objects.create(
                emp_name=e.emp_name, emp_id=e.emp_id, emp_desi=e.emp_desi, emp_rm1=e.emp_rm1, emp_rm2=e.emp_rm2,
                emp_rm3=e.emp_rm3, emp_rm1_id=e.emp_rm1_id, emp_rm2_id=e.emp_rm2_id, emp_rm3_id=e.emp_rm3_id,
                new_rm1=rm1.emp_name, new_rm1_id=rm1.emp_id, new_rm2=rm2.emp_name, new_rm2_id=rm2.emp_id,
                new_rm3=rm3.emp_name, new_rm3_id=rm3.emp_id, emp_process=e.emp_process, new_process=cam.name,
                created_by=request.user.profile.emp_name, created_by_id=request.user.profile.emp_id,
                created_date=datetime.now(), effective_date=date.today(), approved_by='CC TEAM',
                approved_date=datetime.now(), status=True, action='Approved', reason='Approved by CC TEAM',
            )
        e.emp_rm1 = rm1.emp_name
        e.emp_rm1_id = rm1.emp_id
        e.emp_rm2 = rm2.emp_name
        e.emp_rm2_id = rm2.emp_id
        e.emp_rm3 = rm3.emp_name
        e.emp_rm3_id = rm3.emp_id
        e.emp_process = cam.name
        e.emp_process_id = cam.id
        e.emp_desi = desi.name
        e.save()
        messages.success(request, 'Successfully Changed!')
        return redirect(request.META.get('HTTP_REFERER'))
    else:
        messages.error(request, 'Bad Request!')
        return redirect('/ams/dashboard-redirect')


@login_required
def PrintBill(request, pk):
    logged_emp_id = request.user.profile.emp_id
    if logged_emp_id in administration_list:
        try:
            bill = BillAdministration.objects.get(id=pk)
            descriptions = ItemDescriptionAdministration.objects.filter(bill=bill)
            description = []
            for i in descriptions:
                a = {}
                a['description'] = i.description
                a['qty'] = i.qty
                a['price'] = i.price
                a['gst_percent'] = i.gst_percent
                amount_rupees = int(i.amount)
                amount_paise = str(round(i.amount - amount_rupees, 2))[2:4]
                a['amount_rupees'] = amount_rupees
                a['amount_paise'] = amount_paise
                description.append(a)
            gst_rupees = int(bill.gst_amount)
            gst_paise = str(round(bill.gst_amount - gst_rupees, 2))[2:4]
            total_amount_rupees = int(bill.total_amount)
            total_amount_paise = str(round(bill.total_amount - total_amount_rupees, 2))[2:4]
            grand_total_rupees = int(bill.grand_total)
            grand_total_paise = str(round(bill.grand_total - grand_total_rupees, 2))[2:4]
            data = {'bill': bill, 'description': description, 'gst_rupees': gst_rupees, 'gst_paise': gst_paise,
                    'total_amount_rupees': total_amount_rupees, 'total_amount_paise': total_amount_paise,
                    'grand_total_rupees': grand_total_rupees, 'grand_total_paise': grand_total_paise}
            return render(request, 'ams/administration/bill.html', data)
        except BillAdministration.DoesNotExist:
            messages.error(request, 'Bad Request')
            return redirect('/ams/dashboard-redirect')
    else:
        messages.error(request, 'Unauthorized Access!')
        return redirect('/ams/dashboard-redirect')

@login_required
def CreateBill(request):
    logged_emp_id = request.user.profile.emp_id
    if logged_emp_id in administration_list:
        if request.method == "POST":
            project = request.POST["project"]
            category = request.POST["category"]
            date = request.POST["date"]
            po_no = request.POST["po_no"]
            delivery = request.POST["delivery"]
            if delivery == 'old':
                delivery_office = 'Expert Callers Solutions Pvt Ltd'
                delivery_address = '# 18774/4, HBR Layout, 2nd Block 1st Stage, 80ft Main Road, Bangalore - 560043'
            else:
                delivery_office = 'Expert Callers Solutions Pvt Ltd'
                delivery_address = 'Indraprastha, Gubbi cross, 1st Main Rd, Kuvempu Layout, Kothanur, Bengaluru, Karnataka 560077'

            billing = request.POST["billing"]
            if billing == 'old':
                billing_office = '# 18774/4, HBR Layout, 2nd Block 1st Stage, 80ft Main Road, Bangalore - 560043'
            else:
                billing_office = 'Indraprastha, Gubbi cross, 1st Main Rd, Kuvempu Layout, Kothanur, Bengaluru, Karnataka 560077'

            contact_person = request.POST["del_contact_name"]
            contact_no = request.POST["del_contact_no"]
            contact_email = request.POST["del_email"]
            supplier = request.POST["supplier"]
            if supplier == 'other':
                supplier_name = request.POST.get("sup_name")
                sup_address = request.POST.get("sup_address")
                sup_contact_person = request.POST.get("sup_contact_person")
                sup_contact_no = request.POST.get("sup_contact_no")
                sup_contact_email = request.POST.get("sup_contact_email")
                sup_pan = request.POST.get("sup_pan")
                sup_gst = request.POST.get("sup_gst")
                acc_name = request.POST.get("acc_name")
                acc_no = request.POST.get("acc_no")
                acc_bank = request.POST.get("acc_bank")
                bank_branch = request.POST.get("bank_branch")
                bank_ifsc = request.POST.get("bank_ifsc")
                cin_code = request.POST.get("cin_code")
                SupplierAdministration.objects.create(
                    name=supplier_name, address=sup_address, cantact_person=sup_contact_person,
                    contact_no=sup_contact_no, contact_email=sup_contact_email, pan=sup_pan, gst=sup_gst,
                    acc_name=acc_name, acc_no=acc_no, bank_name=acc_bank, bank_branch=bank_branch, ifsc=bank_ifsc,
                    cin_code=cin_code,
                )
            else:
                supplier = SupplierAdministration.objects.get(id=supplier)
                supplier_name = supplier.name
                sup_address = supplier.address
                sup_contact_person = supplier.cantact_person
                sup_contact_no = supplier.contact_no
                sup_contact_email = supplier.contact_email
                sup_pan = supplier.pan
                sup_gst = supplier.gst
                acc_name = supplier.acc_name
                acc_no = supplier.acc_no
                acc_bank = supplier.bank_name
                bank_branch = supplier.bank_branch
                bank_ifsc = supplier.ifsc
                cin_code = supplier.cin_code
            terms = request.POST["terms"]
            terms = terms.replace('\n', '<br>')
            bill = BillAdministration.objects.create(
                project=project, po_no=po_no, date=date, supplier=supplier_name, delivery_office=delivery_office,
                delivery_address=delivery_address, contact_person=contact_person, contact_no=contact_no,
                contact_email=contact_email, terms_conditions=terms, billing_office=billing_office,
                supplier_address=sup_address, supplier_contact_person=sup_contact_person,
                supplier_contact_no=sup_contact_no, supplier_contact_email=sup_contact_email, supplier_pan=sup_pan,
                supplier_gst=sup_gst, acc_name=acc_name, acc_no=acc_no, bank_name=acc_bank, bank_branch=bank_branch,
                ifsc=bank_ifsc, cin_code=cin_code, category=category
            )
            num_of_desc = int(request.POST["num_of_desc"])
            for i in range(1, num_of_desc + 1):
                bill = bill
                description = request.POST.get('description_'+str(i))
                qty = int(request.POST.get('qty_'+str(i)))
                gst_percent = int(request.POST.get('des_gst_'+str(i)))
                price = float(request.POST.get('price_'+str(i)))
                amount = qty * price
                gst_amount = (amount * gst_percent)/100
                ItemDescriptionAdministration.objects.create(
                    bill=bill, description=description, qty=qty, price=price, amount=amount, gst_percent=gst_percent,
                    gst_amount=gst_amount
                )
            total_amount = 0
            gst_amount = 0
            for i in ItemDescriptionAdministration.objects.filter(bill=bill):
                total_amount += i.amount
                gst_amount += i.gst_amount
            grand_total = total_amount + gst_amount
            grand_total = round(grand_total, 2)
            amount_words = num2words(grand_total, lang='en_IN')
            amount_words = amount_words.replace(',', '')
            bill.total_amount = total_amount
            bill.gst_amount = gst_amount
            bill.grand_total = grand_total
            bill.amount_words = amount_words
            bill.save()
            first = LastEmpId.objects.first()
            po_no = LastEmpId.objects.exclude(id=first.id)
            for i in po_no:
                i.emp_id = int(i.emp_id) + 1
                i.save()
            return redirect('/ams/view-bills')
        else:
            first = LastEmpId.objects.first()
            po_no = LastEmpId.objects.exclude(id=first.id)
            for i in po_no:
                po_no = '%.2d' % int(i.emp_id)
            num = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]
            suppliers = SupplierAdministration.objects.all()
            data = {'suppliers': suppliers, 'po': po_no, 'num':num}
            return render(request, 'ams/administration/create_bill.html', data)

    else:
        messages.error(request, 'Unauthorized Access!')
        return redirect('/ams/dashboard-redirect')

@login_required
def getSupplier(request):
    logged_emp_id = request.user.profile.emp_id
    if logged_emp_id in administration_list:
        id = request.POST['id']
        supplier = SupplierAdministration.objects.get(id=id)
        dic = {}
        dic['name'] = str(supplier.name)
        dic['address'] = str(supplier.address)
        dic['cantact_person'] = str(supplier.cantact_person)
        dic['contact_no'] = str(supplier.contact_no)
        dic['contact_email'] = str(supplier.contact_email)
        dic['pan'] = str(supplier.pan)
        dic['gst'] = str(supplier.gst)
        dic['acc_name'] = str(supplier.acc_name)
        dic['acc_no'] = str(supplier.acc_no)
        dic['bank_name'] = str(supplier.bank_name)
        dic['bank_branch'] = str(supplier.bank_branch)
        dic['ifsc'] = str(supplier.ifsc)
        dic['cin_code'] = str(supplier.cin_code)
        return HttpResponse(json.dumps(dic))
    else:
        messages.error(request, 'Unauthorized Access!')
        pass

@login_required
def getWords(request):
    logged_emp_id = request.user.profile.emp_id
    if logged_emp_id in administration_list:
        amount = request.POST['amount']
        amount_words = num2words(amount, lang='en_IN')
        amount_words = amount_words.replace(',', '')
        return HttpResponse(amount_words)
    else:
        messages.error(request, 'Unauthorized Access!')
        pass

@login_required
def ViewBill(request):
    logged_emp_id = request.user.profile.emp_id
    if logged_emp_id in administration_list:
        bills = BillAdministration.objects.all()
        data = {'bills': bills}
        return render(request, 'ams/administration/view_bills.html', data)
    else:
        messages.error(request, 'Unauthorized Access!')
        return redirect('/ams/dashboard-redirect')

@login_required
def ViewSuppliers(request):
    logged_emp_id = request.user.profile.emp_id
    if logged_emp_id in administration_list:
        if request.method == "POST":
            type = request.POST["type"]
            sup_name = request.POST.get("sup_name")
            sup_address = request.POST.get("sup_address")
            sup_contact_person = request.POST.get("sup_contact_person")
            sup_contact_no = request.POST.get("sup_contact_no")
            sup_contact_email = request.POST.get("sup_contact_email")
            sup_pan = request.POST.get("sup_pan")
            sup_gst = request.POST.get("sup_gst")
            acc_name = request.POST.get("acc_name")
            acc_no = request.POST.get("acc_no")
            acc_bank = request.POST.get("acc_bank")
            bank_branch = request.POST.get("bank_branch")
            bank_ifsc = request.POST.get("bank_ifsc")
            cin_code = request.POST.get("cin_code")
            if type == 'add':
                SupplierAdministration.objects.create(
                    name=sup_name, address=sup_address, cantact_person=sup_contact_person, contact_no=sup_contact_no,
                    contact_email=sup_contact_email, pan=sup_pan, gst=sup_gst, acc_name=acc_name, acc_no=acc_no,
                    bank_name=acc_bank, bank_branch=bank_branch, ifsc=bank_ifsc, cin_code=cin_code,
                )
            elif type == 'edit':
                id = request.POST["id"]
                supplier = SupplierAdministration.objects.get(id=id)
                supplier.name = sup_name
                supplier.address = sup_address
                supplier.cantact_person = sup_contact_person
                supplier.contact_no = sup_contact_no
                supplier.contact_email = sup_contact_email
                supplier.pan = sup_pan
                supplier.gst = sup_gst
                supplier.acc_name = acc_name
                supplier.acc_no = acc_no
                supplier.bank_name = acc_bank
                supplier.bank_branch = bank_branch
                supplier.ifsc = bank_ifsc
                supplier.cin_code = cin_code
                supplier.save()
            else:
                messages.error(request, 'Bad Request!')
                return redirect('/ams/')
            return redirect('/ams/view-suppliers')
        else:
            suppliers = SupplierAdministration.objects.all()
            data = {'suppliers': suppliers}
            return render(request, 'ams/administration/view_suppliers.html', data)
    else:
        messages.error(request, 'Unauthorized Access!')
        return redirect('/ams/dashboard-redirect')

@login_required
def ExitRequest(request):
    profile = request.user.profile
    if request.method == 'POST':
        reason = request.POST['reason']
        EmpSeparation.objects.create(
            profile=profile, date=date.today(), reason=reason, status='Applied and waiting for RM1 Approval'
        )
        return redirect('/ams/separation-request')
    else:
        requested = EmpSeparation.objects.filter(profile=profile).first()
        data = {'requested': requested}
        return render(request, 'ams/exit/exit_request.html', data)

@login_required
def ViewExitRequest(request):
    profile = request.user.profile
    if request.method == 'POST':
        id = request.POST['id']
        rm = request.POST['rm']
        comments = request.POST['comments']
        approval = request.POST['approval']
        e = EmpSeparation.objects.get(id=id)
        if rm == 'rm1':
            e.rm1_comment = comments
            if approval == 'Approved':
                e.rm1_approval = True
                e.status = 'Approved by RM1 and waiting for RM2 Approval'
            else:
                e.status = 'Rejected by RM1'
        if rm == 'rm2':
            e.rm2_comment = comments
            if approval == 'Approved':
                e.rm2_approval = True
                e.status = 'Approved by RM2 and waiting for RM3 Approval'
            else:
                e.status = 'Rejected by RM2'
        if rm == 'rm3':
            e.rm3_comment = comments
            if approval == 'Approved':
                e.rm3_approval = True
                e.status = 'Approved by RM3 and waiting for Admin team Approval'
            else:
                e.status = 'Rejected by RM3'
        e.save()
        return redirect('/ams/view-exit-request-rm')

    else:
        all_requests = EmpSeparation.objects.filter(
            Q(profile__emp_rm1_id=profile.emp_id) | Q(profile__emp_rm2_id=profile.emp_id) | Q(profile__emp_rm3_id=profile.emp_id)
        )
        requests = []
        for i in all_requests:
            rm = ''
            dic = {}
            if i.profile.emp_rm1_id == profile.emp_id and i.rm1_approval == False:
                rm = 'rm1'
            elif i.profile.emp_rm2_id == profile.emp_id and i.rm2_approval == False:
                rm = 'rm2'
            elif i.profile.emp_rm3_id == profile.emp_id and i.rm3_approval == False:
                rm = 'rm3'
            dic['request'] = i
            dic['rm'] = rm
            requests.append(dic)
        data = {'requests': requests}
        return render(request, 'ams/exit/view_requests.html', data)

@login_required
def startLogin(request):
    if request.method == "POST":
        emp_id = request.POST['emp_id']
        profile = Profile.objects.get(emp_id=emp_id)
        try:
            LoginHistory.objects.get(profile=profile, date=date.today())
            messages.info(request, "Your had already Logged in and then Logged Out for Today! Can't Login again.")
        except LoginHistory.DoesNotExist:
            LoginHistory.objects.create(
                profile=profile, date=date.today(), login=datetime.now()
            )
        return redirect('/ams/dashboard-redirect')
    else:
        messages.info(request, 'Invalid Request')
        return redirect("/")


@login_required
def stopLogin(request):
    if request.method == "POST":
        id = request.POST['id']
        login = LoginHistory.objects.get(id=id)
        login.done = True
        login.logout = datetime.now()
        login.save()
        return redirect('/ams/dashboard-redirect')
    else:
        messages.info(request, 'Invalid Request')
        return redirect("/")


def addSOP(request):
    if request.method == "POST":
        pass
    else:
        profiles = Profile.objects.filter(agent_status='Active')
        tl_above = Profile.objects.filter(Q(emp_desi__in=manager_list) | Q(emp_desi__in=tl_am_list), agent_status='Active')
        data = {'profiles': profiles, 'tl_above': tl_above}
        return render(request, 'ams/sop/add_sop.html', data)


def addAttendance(request):
    mydate = date.today()
    month = mydate.month
    year = mydate.year
    start_date = date(year, month, 1)
    start_date += monthdelta.monthdelta(1)
    last = start_date + monthdelta.monthdelta(1)
    last_date = last - timedelta(days=1)
    delta = last_date - start_date
    date_list = []

    for i in range(delta.days + 1):
        day = start_date + timedelta(days=i)
        date_list.append(day)

    for i in date_list:
        cal_obj = EcplCalander.objects.filter(date=i)
        emp_ids = []
        for k in cal_obj:
            emp_ids.append(k.emp_id)

        profile = Profile.objects.exclude(Q(emp_id__in=emp_ids) | Q(agent_status='Attrition'))

        cal = []
        for j in profile:
            employees = EcplCalander()
            employees.date = i
            employees.emp_id = j.emp_id
            if j.agent_status == 'Bench':
                employees.att_actual = 'Bench'
            elif j.agent_status == 'NCNS':
                employees.att_actual = 'NCNS'
            else:
                employees.att_actual = 'Unmarked'
            employees.emp_name = j.emp_name
            employees.emp_desi = j.emp_desi
            employees.team = j.emp_process
            employees.team_id = j.emp_process_id
            employees.rm1 = j.emp_rm1
            employees.rm2 = j.emp_rm2
            employees.rm3 = j.emp_rm3
            employees.rm1_id = j.emp_rm1_id
            employees.rm2_id = j.emp_rm2_id
            employees.rm3_id = j.emp_rm3_id
            cal.append(employees)
        EcplCalander.objects.bulk_create(cal)

    return redirect('/ams/')


def autoApproveLeave(request):  # Test 1, 2
    leaves = LeaveTable.objects.filter(Q(tl_approval=False) | Q(manager_approval=False), Q(escalation=False))
    leave_list = []
    ecpl_cal = []
    for i in leaves:
        profile = Profile.objects.get(emp_id=i.emp_id)
        start_date = i.start_date
        end_date = i.end_date
        current_date = datetime.now(pytz.timezone('Asia/Kolkata'))
        # converting into required format
        applied_date = datetime.date(i.applied_date)
        current_date = datetime.date(current_date)
        days = (current_date - applied_date).days
        # Update or Create calander for Leaves
        def updateOrCreateCalander(start_date,end_date):            
            while start_date <= end_date:
                try:
                    j = EcplCalander.objects.get(emp_id=i.emp_id, date=start_date)
                    j.att_actual = i.leave_type
                    j.approved_on = datetime.now()
                    j.appoved_by = "Auto Approved"
                    j.rm1 = profile.emp_rm1
                    j.rm1_id = profile.emp_rm1_id
                    j.rm2 = profile.emp_rm2
                    j.rm2_id = profile.emp_rm2_id
                    j.rm3 = profile.emp_rm3
                    j.rm3_id = profile.emp_rm3_id
                    ecpl_cal.append(j)
                except EcplCalander.DoesNotExist:
                    EcplCalander.objects.create(
                        emp_id=profile.emp_id, date=start_date, att_actual=i.leave_type,
                        approved_on=datetime.now(), appoved_by="Auto Approved", rm1=profile.emp_rm1,
                        rm1_id=profile.emp_rm1_id, rm2=profile.emp_rm2, rm2_id=profile.emp_rm2_id,
                        rm3=profile.emp_rm3, rm3_id=profile.emp_rm3_id, emp_desi=profile.emp_desi,
                        team=profile.emp_process, team_id=profile.emp_process_id, emp_name=profile.emp_name
                    )
                start_date += timedelta(days=1)

        if days > 2:
            if i.tl_approval == False:
                i.tl_approval = True
                i.tl_status = "Auto Approved" 
                i.tl_reason = "Auto Approved"
                i.manager_status = "Auto Approved" 
                i.manager_reason = "Auto Approved"
                i.status = "Auto Approved"
                i.manager_approval = True
                leave_list.append(i)
                updateOrCreateCalander(start_date, end_date)
            else:                
                if i.tl_status == "Rejected":
                    i.manager_status = "Auto Rejected"
                    i.manager_reason = "Rejected by RM1"
                    i.status = "Rejected"
                    i.manager_approval = True
                    leave_list.append(i)
                else:    
                    i.manager_status = "Auto Approved" 
                    i.manager_reason = "Auto Approved"
                    i.status = "Auto Approved"
                    i.manager_approval = True
                    leave_list.append(i)  
                    updateOrCreateCalander(start_date,end_date)          

    LeaveTable.objects.bulk_update(leave_list, ['tl_approval', 'tl_status', 'tl_reason', 'manager_approval',
                                                'manager_status', 'manager_reason', 'status'])
    EcplCalander.objects.bulk_update(ecpl_cal, ['att_actual', 'approved_on', 'appoved_by', 'rm1', 'rm1_id', 'rm2',
                                               'rm2_id', 'rm3', 'rm3_id'])
    return redirect('/ams/')


def addLeaveBalanceMonthly(request,a):
    if a == "3cpl@2022$":
        # Start Date and End Date
        e = date.today()
        month = e.month
        year = e.year
        start_date = date(year, month, 1)
        start_date = start_date - monthdelta.monthdelta(1)
        end_date = date(year, month, 1)
        end_date = end_date - timedelta(days=1)   
        # Collect all employee ID's if not created already
        lst = []
        for i in EmployeeLeaveBalance.objects.exclude(unique_id= month):
            lst.append(i.emp_id)
        # PL and SL Balance calculator
        def plSlCalculator(emp_id):
            full_day_count = EcplCalander.objects.filter(Q(emp_id=emp_id),Q(date__range=[start_date, end_date]),Q(att_actual__in =['present','Week OFF','Comp OFF','Client OFF','Training','PL','SL','ML'])).count()
            half_day_count = EcplCalander.objects.filter(Q(emp_id=emp_id),Q(date__range=[start_date, end_date]),Q(att_actual = 'Half Day')).count()
            earned = full_day_count+(half_day_count/2)
            pl_balance = round(earned/20,2)
            sl_balance = 1 if pl_balance > 0 else 0
            return(pl_balance,sl_balance)

        for i in lst:
            e = EmployeeLeaveBalance.objects.get(emp_id = i)
            pl_balance , sl_balance = plSlCalculator(i)
            ini = e.pl_balance + e.sl_balance      
            e.pl_balance += pl_balance
            e.sl_balance += sl_balance
            e.unique_id = month     
            e.save()
            # Creating Leave History's
            def createHistory(emp_id,lt,lc,total):
                l_hist = leaveHistory()
                l_hist.emp_id = emp_id
                l_hist.date = date.today()
                l_hist.leave_type = lt
                l_hist.transaction = "Leaves Earned"
                l_hist.no_days = lc
                l_hist.total = total
                l_hist.save()
            if pl_balance > 0:
                total = pl_balance+ini
                createHistory(i, 'PL', pl_balance, total)
                createHistory(i, 'SL', sl_balance, total=total+sl_balance)
        # Bulk upload/Create leave balance/history 
        return redirect('/ams/')
    else:
        messages.success(request, "Unauthorized Access")
        return redirect('/ams/')

def newsandwichpolicy(request):

    import datetime as dt
    previous_month = (dt.date.today().replace(day=1) - dt.timedelta(days=1)).month

    # month_days = []  
    # year = 2022
    # month = 6
    # a, num_days = calendar.monthrange(year, month)
    # start_date = date(year, month, 1)
    # end_date = date(year, month, num_days)
    # delta = timedelta(days=1)
    # while start_date <= end_date:
    #     month_days.append(start_date)
    #     start_date += delta
    # ids = []
    # emps = EmployeeLeaveBalance.objects.filter(unique_id=6)
    # for i in emps:
    #     ids.append(i.emp_id)

    leaves_list= []
    leaves = EcplCalander.objects.filter(Q(att_actual__in = ['PL','SL','Absent','Unmarked']),Q(date__month=previous_month))
    for i in leaves:
        d = {}      
        d['date']= i.date
        d['emp_id'] = i.emp_id
        leaves_list.append(d)

    off_list = []
    offs = EcplCalander.objects.filter(Q(att_actual__in=['Week OFF','Comp OFF']),Q(date__month=6))
    for i in offs:
        d={}
        d['date']=i.date
        d['emp_id']=i.emp_id
        off_list.append(d)

    # Sandwich master list
    sand = []
    for i in leaves_list:
        eid = i['emp_id']
        edate = i['date']
        nextdate = edate + timedelta(days=1)
        d = nextdate
        for j in off_list:
            while j['date'] == d and j['emp_id']== eid:
                d = d + timedelta(days=1)

        if (d-edate).days >1:
            for j in leaves_list:
                if j['emp_id'] == eid and j['date']== d:
                    di = {}
                    di['start'] = edate
                    di['end'] = d
                    di['emp_id'] = eid
                    sand.append(di)
                    # print('sandwich between/emp_id ', edate,d,eid)
                else:     
                    pass
    # data = {'sand':sand}
    # return render(request,'ams/sandwich.html',data)
    
    for i in sand:
        cal = EcplCalander.objects.filter(emp_id=i['emp_id'], date__gt =i['start'],date__lt=i['end'])
        for j in cal:
            j.att_actual = 'Absent'
            j.save()
    return redirect('/ams/')




def TestFun(request):
    return redirect("/ams/")