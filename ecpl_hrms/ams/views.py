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

tl_am_list = ['Team Leader','Assistant Manager', 'Subject Matter Expert', 'Trainer','Learning and Development Head',
              'Process Trainer','Trainer Sales',
              ]

manager_list = ['Quality Head','Operations Manager','Service Delivery Manager','Command Centre Head']

hr_list = ['HR','HR Manager','Manager ER','HR Lead','Sr Recruiter','MIS Executive HR',
'Lead HRBP','Employee Relations Specialist','Payroll Specialist','Recruiter','HR Generalist']

agent_list = [ 'Client Relationship Officer ','MIS Executive','Patrolling officer',
               'Data Analyst','Business Development Executive','Content Developer',
               'Junior Developer','Web Developer','Trainee Developer',
               'Jr Dev',
                ]

# Create your views here.
def loginPage(request):
    logout(request)
    form = AuthenticationForm()
    teams = Campaigns.objects.all().order_by('name')

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

            if request.user.profile.emp_desi in tl_am_list:
                return redirect('/ams/tl-dashboard')

            elif request.user.profile.emp_desi in manager_list:
                return redirect('/ams/manager-dashboard')

            elif request.user.profile.emp_desi in hr_list:
                return redirect('/ams/hr-dashboard')
            else:
                return redirect('/ams/agent-dashboard')
        else:
            form = AuthenticationForm()
            messages.info(request,'Invalid Credentials')
            teams = Campaigns.objects.all().order_by('name')
            data = {'teams': teams, 'form': form}
            return render(request, 'ams/login.html', data)
    else:
        logout(request)
        form = AuthenticationForm()
        teams = Campaigns.objects.all().order_by('name')
        data = {'teams': teams, 'form': form}
        return render(request, 'ams/login.html', data)

@login_required
def redirectTOAllDashBoards(request,id):

    if request.user.profile.emp_desi in tl_am_list:
        return redirect('/ams/tl-dashboard')
    elif request.user.profile.emp_desi in hr_list:
        return redirect('/ams/hr-dashboard')
    else:
        return HttpResponse('<h1>Not Authorised</h1>')


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


@login_required
def agentDashBoard(request):

    if request.user.profile.emp_desi in agent_list:

        emp_name = request.user.profile.emp_name
        emp_id = request.user.profile.emp_id
        emp = Employee.objects.get(emp_id = emp_id)
        #attendance status
        cal = LeaveTable.objects.filter(Q(emp_id=emp_id),Q(leave_type__in=['SL','PL'])).order_by('-applied_date')[:5]

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
                st = EcplCalander.objects.get(Q(date=i),Q(emp_id = emp_id)).att_actual

            except EcplCalander.DoesNotExist:
                st = 'Unmarked'
            dict['dt'] = i
            dict['st'] = st
            month_cal.append(dict)

        data = {'emp':emp,'cal':cal,'month_cal':month_cal}

        return render(request,'ams/agent-dashboard-new.html',data)
    else:
        return HttpResponse('<H1>You are not Authorised to view this page ! </H1>')

@login_required
def tlDashboard(request):
    usr_desi = request.user.profile.emp_desi
    if usr_desi in tl_am_list:
        emp_name = request.user.profile.emp_name
        emp_id = request.user.profile.emp_id
        emp = Employee.objects.get(emp_id=emp_id)
        #All Employees
        all_emp = Employee.objects.filter(Q(agent_status = 'Active'),Q(emp_rm1=emp_name) | Q(emp_rm2=emp_name) | Q(emp_rm3=emp_name))
        # details
        today = date.today()
        today = str(today)
        # All Active Today
        att_details = EcplCalander.objects.filter(date = today,rm1=emp_name)
        #counts
        emp_count = Employee.objects.filter(Q(agent_status = 'Active'),Q(emp_rm1=emp_name) | Q(emp_rm2=emp_name) | Q(emp_rm3=emp_name)).distinct().count()
        present_count = EcplCalander.objects.filter(Q(rm1=emp_name) | Q(rm2=emp_name) | Q(rm3=emp_name),Q(date=today),Q(att_actual='present')).count()
        absent_count = EcplCalander.objects.filter(Q(rm1=emp_name) | Q(rm2=emp_name) | Q(rm3=emp_name), Q(date=today), Q(att_actual='Absent')).count()
        week_off_count = EcplCalander.objects.filter(Q(rm1=emp_name) | Q(rm2=emp_name) | Q(rm3=emp_name), Q(date=today), Q(att_actual='Week OFF')).count()
        comp_off_count = EcplCalander.objects.filter(Q(rm1=emp_name) | Q(rm2=emp_name) | Q(rm3=emp_name), Q(date=today), Q(att_actual='Comp OFF')).count()
        half_day_count = EcplCalander.objects.filter(Q(rm1=emp_name) | Q(rm2=emp_name) | Q(rm3=emp_name), Q(date=today), Q(att_actual='Half Day')).count()
        holiday_count = EcplCalander.objects.filter(Q(rm1=emp_name) | Q(rm2=emp_name) | Q(rm3=emp_name), Q(date=today), Q(att_actual='Holiday')).count()
        sl_count = EcplCalander.objects.filter(Q(rm1=emp_name) | Q(rm2=emp_name) | Q(rm3=emp_name), Q(date=today), Q(att_actual='SL')).count()
        pl_count = EcplCalander.objects.filter(Q(rm1=emp_name) | Q(rm2=emp_name) | Q(rm3=emp_name), Q(date=today), Q(att_actual='PL')).count()
        attrition_count = EcplCalander.objects.filter(Q(rm1=emp_name) | Q(rm2=emp_name) | Q(rm3=emp_name), Q(date=today), Q(att_actual='Attrition')).count()
        training_count = EcplCalander.objects.filter(Q(rm1=emp_name) | Q(rm2=emp_name) | Q(rm3=emp_name), Q(date=today), Q(att_actual='Training')).count()

        unmarked_count = emp_count - (present_count + absent_count + week_off_count + comp_off_count + half_day_count + holiday_count + sl_count + pl_count + attrition_count + training_count)
        # Mapping Tickets >>
        map_tickets_counts = MappingTickets.objects.filter(new_rm3 = emp_name,status=False).count()

        #Leaves
        leave_req_count = LeaveTable.objects.filter(emp_rm1 = emp_name,tl_approval = False).count()

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
                st = EcplCalander.objects.get(Q(date=i), Q(emp_id=emp_id)).att_actual

            except EcplCalander.DoesNotExist:
                st = 'Unmarked'
            dict['dt'] = i
            dict['st'] = st
            month_cal.append(dict)


        data = {'emp_name': emp_name, 'emp': emp, 'att_details':att_details,
                'emp_count':emp_count,
                'present_count':present_count,'absent_count':absent_count,'week_off_count':week_off_count,
                'comp_off_count':comp_off_count,'half_day_count':half_day_count,'holiday_count':holiday_count,
                'unmarked_count':unmarked_count,'map_tickets_counts':map_tickets_counts,
                'all_emp':all_emp,'sl_count':sl_count,'pl_count':pl_count,'attrition_count':attrition_count,
                'training_count':training_count,
                'leave_req_count':leave_req_count,
                'month_cal': month_cal,
                }
        return render(request, 'ams/rm-dashboard-new.html', data)
    elif usr_desi in manager_list:
        return redirect('/ams/manager-dashboard')
    elif usr_desi in hr_list:
        return redirect('/ams/hr-dashboard')
    elif usr_desi in agent_list:
        return redirect('/ams/agent-dashboard')
    else:
        return HttpResponse('<H1>You are not Authorised to view this page ! </H1>')

@login_required
def managerDashboard(request):
    if request.user.profile.emp_desi in manager_list:
        mgr_name = request.user.profile.emp_name
        emp_id = request.user.profile.emp_id
        # All Employees
        all_emps = Employee.objects.filter(Q(agent_status = 'Active'),Q(emp_rm1=mgr_name) |Q(emp_rm2=mgr_name) | Q(emp_rm3=mgr_name))
        # count of all employees
        count_all_emps = all_emps.count()

        # TLS
        all_tls = Employee.objects.filter(Q(agent_status = 'Active'),Q(emp_rm1=mgr_name) |Q(emp_rm2=mgr_name) | Q(emp_rm3=mgr_name),Q(emp_desi='Team Leader'))
        # TLS Count
        all_tls_count=all_tls.count()

        # AMS
        all_ams = Employee.objects.filter(Q(agent_status = 'Active'),Q(emp_rm1=mgr_name) | Q(emp_rm2=mgr_name) | Q(emp_rm3=mgr_name),
                                         Q(emp_desi='Assistant Manager'))
        # TLS Count
        all_ams_count = all_ams.count()

        emp= Employee.objects.get(emp_name = mgr_name)

        # All Employees
        all_emp = Employee.objects.filter(Q(agent_status='Active'),
                                          Q(emp_rm1=mgr_name) | Q(emp_rm2=mgr_name) | Q(emp_rm3=mgr_name))

        #Mapping Tickets
        map_tickets_counts = MappingTickets.objects.filter(new_rm3=mgr_name, status=False).count()

        #Leave Requests
        leave_req_count = LeaveTable.objects.filter(emp_rm3=mgr_name,tl_status='Approved',manager_approval=False).count()

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
                st = EcplCalander.objects.get(Q(date=i), Q(emp_id=emp_id)).att_actual

            except EcplCalander.DoesNotExist:
                st = 'Unmarked'
            dict['dt'] = i
            dict['st'] = st
            month_cal.append(dict)


        data = {'emp':emp,'count_all_emps':count_all_emps,
                'all_tls':all_tls,'all_tls_count':all_tls_count,
                'all_ams': all_ams, 'all_ams_count': all_ams_count,
                'map_tickets_counts':map_tickets_counts,
                'leave_req_count':leave_req_count,'all_emp':all_emp,'month_cal':month_cal,
                }
        return render(request,'ams/manager-dashboard.html',data)
    else:
        return HttpResponse('<h1>*** You are not authorised to view this page ***</h1>')

def viewAndApproveLeaveRequestMgr(request):

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
        now=datetime.now()
        start_date = e.start_date
        end_date = e.end_date

        om_response = request.POST['tl_response']
        om_reason = request.POST['tl_reason']

        if om_response == 'Approve':
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
                    cal = EcplCalander.objects.get(date = i,emp_id=emp_id)
                    cal.att_actual = att_actual
                    cal.save()

                except EcplCalander.DoesNotExist:

                    cal = EcplCalander.objects.create(
                            team=team, date=i, emp_id=emp_id,
                            att_actual=att_actual, applied_status=True,
                            rm1=rm1, rm2=rm2, rm3=rm3,
                            approved_on=now, emp_desi=emp_desi, appoved_by=request.user.profile.emp_name,
                            emp_name=emp_name
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

        e.manager_approval = manager_approval
        e.manager_reason = om_reason
        e.manager_status = manager_status
        e.status = status
        e.save()

        return redirect('/ams/view-leave-request-mgr')
    else:

        mgr_name = request.user.profile.emp_name
        emp_id = request.user.profile.emp_id
        emp = Employee.objects.get(emp_id=emp_id)
        leave_request = LeaveTable.objects.filter(emp_rm3=mgr_name,tl_status='Approved',manager_approval=False)

        data = {'emp':emp,'leave_request':leave_request}
        return render(request,'ams/leave_approval_rm3.html',data)

@login_required
def viewallOMS(request,name):
    emp_name = request.user.profile.emp_name
    emp_id = request.user.profile.emp_id
    emp = Employee.objects.get(emp_id=emp_id)

    if name == 'Agent':

        all_emp = Employee.objects.filter(Q(agent_status = 'Active'),Q(emp_rm1=emp_name) | Q(emp_rm2=emp_name) | Q(emp_rm3=emp_name))

        data = {'emp':emp,'all_emp':all_emp}
        return render(request,'ams/view_all_emp_om.html',data)

    elif name == 'TL':
        all_emp = Employee.objects.filter(Q(agent_status = 'Active'),Q(emp_rm1=emp_name) | Q(emp_rm2=emp_name) | Q(emp_rm3=emp_name), Q(emp_desi='Team Leader'))
        data = {'emp': emp, 'all_emp': all_emp}
        return render(request, 'ams/view_all_emp_om.html', data)

    elif name == 'AM':
        all_emp = Employee.objects.filter(Q(agent_status = 'Active'),Q(emp_rm1=emp_name) | Q(emp_rm2=emp_name) | Q(emp_rm3=emp_name), Q(emp_desi='Assistant Manager'))
        data = {'emp': emp, 'all_emp': all_emp}
        return render(request, 'ams/view_all_emp_om.html', data)

    else:

        messages.info(request,'Bad Request')
        return redirect('/ams/tl-dashboard')


@login_required
def hrDashboard(request):
    user_desi = request.user.profile.emp_desi

    if user_desi in hr_list:
        emp_id = request.user.profile.emp_id
        emp = Employee.objects.get(emp_id=emp_id)
        all_users_count = Employee.objects.all().count()
        all_team_count = Campaigns.objects.all().count()
        all_job_count = JobRequisition.objects.all().count()
        teams = Campaigns.objects.all()

        # Att Request Count
        att_requests_count = AttendanceCorrectionHistory.objects.filter(status=False).count()

        data = {'emp':emp,'all_users_count':all_users_count,'all_team_count':all_team_count,
                'all_job_count':all_job_count,'att_requests_count':att_requests_count,
                'team':teams}

        return render(request,'ams/hr_dashboard.html',data)
    else:
        return HttpResponse('<h1>*** You are not authorised to view this page ***</h1>')

@login_required
def on_boarding(request):
    if request.method == "POST":

        hrname = request.user
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
        emp_bank_ifsc = request.POST["emp_bank_ifsc"]        #
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
        e = OnboardingnewHRC()
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
        e.emp_quali_other=emp_quali_other
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
        e.save()

        return redirect("/ams/onboarding")
    else:
        emp_id = request.user.profile.emp_id
        emp = Employee.objects.get(emp_id=emp_id)
        data = {'emp': emp}
        return render(request, 'ams/onboarding.html', data)





@login_required
def viewOnBoarding(request):

    onboard = OnboardingnewHRC.objects.all()
    emp_id = request.user.profile.emp_id
    emp = Employee.objects.get(emp_id=emp_id)

    data = {'onboard':onboard,'emp':emp}
    return render(request, "ams/view_onboarding.html", data)


def on_boarding_update(request,id):
    if request.method == "POST":
        id = request.POST["id"]
        e = OnboardingnewHRC.objects.get(id=id)
        hrname = request.user
        # usrname = request.user.id
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

        #
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
        emp = Employee.objects.get(emp_id=emp_id)
        data = {"onboard": onboard,'emp':emp}
        return render(request, "ams/edit_onboarding.html", data)


@login_required
def addNewUserHR(request):
    if request.method == 'POST':
        on_id = request.POST['id']
        emp_name = request.POST["emp_name"]
        emp_id = request.POST["emp_id"]
        emp_doj = request.POST["emp_doj"]
        emp_desi = request.POST["emp_desg"]
        emp_rm1 = request.POST["emp_rm1"]
        emp_rm2 = request.POST["emp_rm2"]
        emp_rm3 = request.POST["emp_rm3"]
        emp_process = request.POST["emp_pro"]
        usr = User.objects.filter(username=emp_id)
        onb_obj = OnboardingnewHRC.objects.get(id=on_id)

        if usr.exists():
            return HttpResponse('<h1>User Already Exists</h1>')
        else:
            # Creating User
            user = User.objects.create_user(username=emp_id, password=str(emp_id))
            user.save()
            usr = User.objects.get(username=emp_id)
            #Creating Profile
            profile = Profile.objects.create(
                emp_id=emp_id, emp_name=emp_name, emp_desi=emp_desi,
                emp_rm1=emp_rm1, emp_rm2=emp_rm2, emp_rm3=emp_rm3,
                emp_process=emp_process, user=usr,doj=emp_doj,on_id=on_id,
            )
            #creating Employee table(Mapping)
            emp = Employee.objects.create(
                emp_id=emp_id, emp_name=emp_name, emp_desi=emp_desi,
                emp_rm1=emp_rm1, emp_rm2=emp_rm2, emp_rm3=emp_rm3,
                emp_process=emp_process,on_id=on_id,
            )
            onb_obj.user_created = True
            onb_obj.save()
            profile.save()
            emp.save()
        messages.info(request,'User and Profile Successfully Created')
        return redirect('/ams/add-new-user')

    else:
        emp_id = request.user.profile.emp_id
        emp = Employee.objects.get(emp_id=emp_id)
        all_desi = Employee.objects.all().values('emp_desi').distinct().order_by('emp_desi')
        rms = Employee.objects.exclude(emp_desi__in =['Client Relationship Officer','Patrolling Officer']).order_by('emp_name')
        all_team = Campaigns.objects.all()
        onboarding = OnboardingnewHRC.objects.filter(user_created=False)
        data = {'emp': emp,'all_data':all_desi,'rms':rms,'all_team':all_team,'onboarding':onboarding}
        return render(request,'ams/hr_add_user.html',data)
@login_required
def viewUsersHR(request):
    emp_id = request.user.profile.emp_id
    emp = Employee.objects.get(emp_id=emp_id)
    add = Profile.objects.all()
    data = {'add':add,'emp':emp}

    return render(request,'ams/view_user_hr.html',data)

def viewEmployeeProfile(request,id,on_id):

    emp_id = request.user.profile.emp_id
    emp = Employee.objects.get(emp_id=emp_id)

    profile = Profile.objects.get(id=id)

    onboarding = OnboardingnewHRC.objects.get(id=on_id)
    
    data = {'profile': profile, 'onboard': onboarding,'emp':emp}

    return render(request,'ams/emp_profile_view.html',data)

@login_required
def applyAttendace(request):
    if request.method == 'POST':
        ddate = request.POST['date']
        att_actual = request.POST['att_actual']
        emp_name = request.POST['emp_name']
        rm1 = request.POST['rm1']
        rm2 = request.POST['rm2']
        rm3 = request.POST['rm3']
        emp_id = request.POST['emp_id']
        emp_desi = request.POST['emp_desi']
        team = request.POST['emp_team']
        now = datetime.now()
        try:
            cal = EcplCalander.objects.get(date=ddate,emp_id=emp_id)
            messages.info(request,'*** Already Marked in Calendar, Please Refresh the page and try again ***')
            return redirect('/ams/team-attendance')

        except EcplCalander.DoesNotExist:

            cal = EcplCalander.objects.create(
                team = team, date = ddate, emp_id = emp_id,
                att_actual = att_actual,applied_status = True,
                rm1 = rm1, rm2 = rm2, rm3 = rm3,
                approved_on = now, emp_desi = emp_desi,appoved_by = request.user.profile.emp_name,
                emp_name = emp_name
            )

        cal.save()
        return redirect('/ams/team-attendance')
    else:
        return HttpResponse('<h1>*** GET not available ***</h1>')

@login_required
def newSingleAttandance(request):

    if request.method == 'POST':
        ddate = request.POST['date']
        att_actual = request.POST['att_actual']
        emp_name = request.POST['emp_name']
        rm1 = request.POST['rm1']
        rm2 = request.POST['rm2']
        rm3 = request.POST['rm3']
        emp_id = request.POST['emp_id']
        emp_desi = request.POST['emp_desi']
        team = request.POST['emp_team']
        now = datetime.now()

        try:
            cal = EcplCalander.objects.get(date=ddate,emp_id=emp_id)
            messages.info(request,'*** Already Marked in Calendar, Please Refresh the page and try again ***')
            return redirect('/ams/team-attendance')

        except EcplCalander.DoesNotExist:

            cal = EcplCalander.objects.create(
                team=team, date=ddate, emp_id=emp_id,
                att_actual=att_actual, applied_status=True,
                rm1=rm1, rm2=rm2, rm3=rm3,
                approved_on=now, emp_desi=emp_desi, appoved_by=request.user.profile.emp_name,
                emp_name=emp_name
            )

        cal.save()
        return redirect('/ams/ams-update-attendance')

    else:
        ######### Dates #################################
        today = date.today()
        yesterday = today - timedelta(days=1)
        dby_date = yesterday - timedelta(days=1)
        emp_s = Employee.objects.filter(agent_status = 'Active',emp_id=request.user.profile.emp_id)
        ############## Todays Attendance ###################
        todays_list_list = []
        for i in emp_s:
            todays_list = {}
            try:
                cal_day = EcplCalander.objects.get(date=today, applied_status=True, emp_id=i.emp_id)
                tdy_date = today
                todays_list['id'] = i.id
                todays_list['emp_id'] = i.emp_id
                todays_list['name'] = i.emp_name
                todays_list['status'] = 'Applied'
                todays_list['date'] = str(today)
                todays_list['rm1'] = i.emp_rm1
                todays_list['rm2'] = i.emp_rm2
                todays_list['rm3'] = i.emp_rm3
                todays_list['emp_desi'] = i.emp_desi
                todays_list['emp_team'] = i.emp_process

            except EcplCalander.DoesNotExist:
                tdy_date = today
                todays_list['id'] = i.id
                todays_list['emp_id'] = i.emp_id
                todays_list['name'] = i.emp_name
                todays_list['status'] = str(today)
                todays_list['date'] = str(today)
                todays_list['rm1'] = i.emp_rm1
                todays_list['rm2'] = i.emp_rm2
                todays_list['rm3'] = i.emp_rm3
                todays_list['emp_desi'] = i.emp_desi
                todays_list['emp_team'] = i.emp_process

            todays_list_list.append(todays_list)

        ############## Yesterdays Attendance ###################
        ystday_list_list = []
        for i in emp_s:
            ystday_list = {}
            try:
                cal_day = EcplCalander.objects.get(date=yesterday, applied_status=True, emp_id=i.emp_id)
                tdy_date = yesterday
                ystday_list['id'] = i.id
                ystday_list['emp_id'] = i.emp_id
                ystday_list['name'] = i.emp_name
                ystday_list['status'] = 'Applied'
                ystday_list['date'] = str(yesterday)
                ystday_list['rm1'] = i.emp_rm1
                ystday_list['rm2'] = i.emp_rm2
                ystday_list['rm3'] = i.emp_rm3
                ystday_list['emp_desi'] = i.emp_desi
                ystday_list['emp_team'] = i.emp_process

            except EcplCalander.DoesNotExist:
                tdy_date = yesterday
                ystday_list['id'] = i.id
                ystday_list['emp_id'] = i.emp_id
                ystday_list['name'] = i.emp_name
                ystday_list['status'] = str(yesterday)
                ystday_list['date'] = str(yesterday)
                ystday_list['rm1'] = i.emp_rm1
                ystday_list['rm2'] = i.emp_rm2
                ystday_list['rm3'] = i.emp_rm3
                ystday_list['emp_desi'] = i.emp_desi
                ystday_list['emp_team'] = i.emp_process

            ystday_list_list.append(ystday_list)
        ############## Day befor Yesterdays Attendance ###################
        dby_list_list = []
        for i in emp_s:
            dby_list = {}
            try:
                cal_day = EcplCalander.objects.get(date=dby_date, applied_status=True, emp_id=i.emp_id)
                tdy_date = dby_date
                dby_list['id'] = i.id
                dby_list['emp_id'] = i.emp_id
                dby_list['name'] = i.emp_name
                dby_list['status'] = 'Applied'
                dby_list['date'] = str(dby_date)
                dby_list['rm1'] = i.emp_rm1
                dby_list['rm2'] = i.emp_rm2
                dby_list['rm3'] = i.emp_rm3
                dby_list['emp_desi'] = i.emp_desi
                dby_list['emp_team'] = i.emp_process

            except EcplCalander.DoesNotExist:
                tdy_date = dby_date
                dby_list['id'] = i.id
                dby_list['emp_id'] = i.emp_id
                dby_list['name'] = i.emp_name
                dby_list['status'] = str(dby_date)
                dby_list['date'] = str(dby_date)
                dby_list['rm1'] = i.emp_rm1
                dby_list['rm2'] = i.emp_rm2
                dby_list['rm3'] = i.emp_rm3
                dby_list['emp_desi'] = i.emp_desi
                dby_list['emp_team'] = i.emp_process

            dby_list_list.append(dby_list)

        emp_id = request.user.profile.emp_id
        emp = Employee.objects.get(emp_id=emp_id)

        data = {'todays_att': todays_list_list,
                'ystdays_att': ystday_list_list,
                'dbys_att': dby_list_list,'emp':emp}

        return render(request, 'ams/attendance.html', data)


@login_required
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

@login_required
def teamAttendance(request):
    user_nm = request.user.profile.emp_name
    if request.method == 'POST':
        return HttpResponse('<h1>*** POST Not Available ***</h1>')
    else:
        ######### Dates #################################
        today = date.today()
        yesterday = today - timedelta(days=1)
        dby_date = yesterday - timedelta(days=1)
        emp_s = Employee.objects.filter(Q(emp_rm1=user_nm) | Q(emp_rm2=user_nm) | Q(emp_rm3=user_nm),agent_status = 'Active')
        if emp_s.count()<1:
            return HttpResponse('<h1>RM1 name and user name not matching </h1>')
        ############## Todays Attendance ###################
        todays_list_list = []
        for i in emp_s:
            todays_list = {}
            try:
                cal_day = EcplCalander.objects.get(date=today, applied_status=True, emp_id=i.emp_id)
                tdy_date = today
                todays_list['id']=i.id
                todays_list['emp_id']=i.emp_id
                todays_list['name'] = i.emp_name
                todays_list['status'] = 'Applied'
                todays_list['date'] = str(today)
                todays_list['rm1'] = i.emp_rm1
                todays_list['rm2'] = i.emp_rm2
                todays_list['rm3'] = i.emp_rm3
                todays_list['emp_desi'] = i.emp_desi
                todays_list['emp_team'] = i.emp_process

            except EcplCalander.DoesNotExist:
                tdy_date = today
                todays_list['id'] = i.id
                todays_list['emp_id'] = i.emp_id
                todays_list['name'] = i.emp_name
                todays_list['status'] = str(today)
                todays_list['date'] = str(today)
                todays_list['rm1'] = i.emp_rm1
                todays_list['rm2'] = i.emp_rm2
                todays_list['rm3'] = i.emp_rm3
                todays_list['emp_desi'] = i.emp_desi
                todays_list['emp_team'] = i.emp_process

            todays_list_list.append(todays_list)

        ############## Yesterdays Attendance ###################
        ystday_list_list = []
        for i in emp_s:
            ystday_list = {}
            try:
                cal_day = EcplCalander.objects.get(date=yesterday, applied_status=True, emp_id=i.emp_id)
                tdy_date = yesterday
                ystday_list['id']=i.id
                ystday_list['emp_id']=i.emp_id
                ystday_list['name'] = i.emp_name
                ystday_list['status'] = 'Applied'
                ystday_list['date'] = str(yesterday)
                ystday_list['rm1'] = i.emp_rm1
                ystday_list['rm2'] = i.emp_rm2
                ystday_list['rm3'] = i.emp_rm3
                ystday_list['emp_desi'] = i.emp_desi
                ystday_list['emp_team'] = i.emp_process

            except EcplCalander.DoesNotExist:
                tdy_date = yesterday
                ystday_list['id'] = i.id
                ystday_list['emp_id'] = i.emp_id
                ystday_list['name'] = i.emp_name
                ystday_list['status'] = str(yesterday)
                ystday_list['date'] = str(yesterday)
                ystday_list['rm1'] = i.emp_rm1
                ystday_list['rm2'] = i.emp_rm2
                ystday_list['rm3'] = i.emp_rm3
                ystday_list['emp_desi'] = i.emp_desi
                ystday_list['emp_team'] = i.emp_process

            ystday_list_list.append(ystday_list)

        ############## Bay befor Yesterdays Attendance ###################
        dby_list_list = []
        for i in emp_s:
            dby_list = {}
            try:
                cal_day = EcplCalander.objects.get(date=dby_date, applied_status=True, emp_id=i.emp_id)
                tdy_date = dby_date
                dby_list['id']=i.id
                dby_list['emp_id']=i.emp_id
                dby_list['name'] = i.emp_name
                dby_list['status'] = 'Applied'
                dby_list['date'] = str(dby_date)
                dby_list['rm1'] = i.emp_rm1
                dby_list['rm2'] = i.emp_rm2
                dby_list['rm3'] = i.emp_rm3
                dby_list['emp_desi'] = i.emp_desi
                dby_list['emp_team'] = i.emp_process

            except EcplCalander.DoesNotExist:
                tdy_date = dby_date
                dby_list['id'] = i.id
                dby_list['emp_id'] = i.emp_id
                dby_list['name'] = i.emp_name
                dby_list['status'] = str(dby_date)
                dby_list['date'] = str(dby_date)
                dby_list['rm1'] = i.emp_rm1
                dby_list['rm2'] = i.emp_rm2
                dby_list['rm3'] = i.emp_rm3
                dby_list['emp_desi'] = i.emp_desi
                dby_list['emp_team'] = i.emp_process

            dby_list_list.append(dby_list)

        emp_id = request.user.profile.emp_id
        emp = Employee.objects.get(emp_id=emp_id)

        data = {'todays_att':todays_list_list,
                'ystdays_att':ystday_list_list,
                'dbys_att':dby_list_list,'emp':emp}

        return render(request,'ams/team_attendance.html',data)

@login_required
def viewTeamAttendance(request):

    if request.method == 'POST':
        rm = request.user.profile.emp_name
        start_date = request.POST['start_date']
        end_date = request.POST['end_date']
        emp_id = request.POST['emp_id']

        start_date = start_date
        end_date = end_date
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        delta = end_date - start_date  # returns timedelta

        date_list = []
        for i in range(delta.days + 1):
            day = start_date + timedelta(days=i)
            date_list.append(day)


        if emp_id == 'All':


            all_emp = Employee.objects.filter(Q(agent_status = 'Active'),Q(emp_rm1=rm) | Q(emp_rm2=rm) | Q(emp_rm3=rm))

            agt_cal_list = []

            for k in date_list:

                for j in all_emp:

                    agt_cal = {}

                    try:
                        agt_calendar = EcplCalander.objects.get(date=k, emp_id=j.emp_id)
                        agt_cal['date'] = k
                        agt_cal['status'] = agt_calendar.att_actual
                        agt_cal['approved_on'] = agt_calendar.approved_on
                        agt_cal['team'] = agt_calendar.team
                        agt_cal['emp_name'] = agt_calendar.emp_name


                    except EcplCalander.DoesNotExist:
                        agt_cal['date'] = k
                        agt_cal['status'] = 'Unmarked'
                        agt_cal['approved_on'] = 'NA'
                        agt_cal['team'] = j.emp_process
                        agt_cal['emp_name'] = j.emp_name


                    agt_cal_list.append(agt_cal)

            emp_id = request.user.profile.emp_id
            emp = Employee.objects.get(emp_id=emp_id)

            data = {'agt_cal_list': agt_cal_list,
                        'emp': emp}

            return render(request, 'ams/agent-calander-status.html', data)

        emp_obj = Employee.objects.get(emp_id=emp_id)
        agt_cal_list = []

        for i in date_list:
            agt_cal = {}
            try:
                agt_calendar = EcplCalander.objects.get(date=i, emp_id=emp_id)
                agt_cal['date']=i
                agt_cal['status']=agt_calendar.att_actual
                agt_cal['approved_on'] = agt_calendar.approved_on
                agt_cal['team'] = agt_calendar.team
                agt_cal['emp_name'] = agt_calendar.emp_name

            except EcplCalander.DoesNotExist:
                agt_cal['date'] = i
                agt_cal['status'] = 'Unmarked'
                agt_cal['approved_on'] = 'NA'
                agt_cal['team'] = 'NA'
                agt_cal['emp_name'] = emp_obj.emp_name

            agt_cal_list.append(agt_cal)

        emp_id = request.user.profile.emp_id
        emp = Employee.objects.get(emp_id=emp_id)

        data = {'agt_cal_list':agt_cal_list,
                'emp':emp}

        return render(request,'ams/agent-calander-status.html',data)

    else:
        return HttpResponse('<h2>*** GET not available ***</h2>')

@login_required
def teamAttendanceReport(request):

    if request.method == 'POST':

        start_date = request.POST['start_date']
        end_date = request.POST['end_date']
        team_name = request.POST['team_name']
        start_date = start_date
        end_date = end_date
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        delta = end_date - start_date  # returns timedelta
        date_list = []

        for i in range(delta.days + 1):
            day = start_date + timedelta(days=i)
            date_list.append(day)

        if team_name == 'All Team':

            agt_cal_list = []
            agent_list = []
            agents = Employee.objects.all()

            for i in agents:
                agent_list.append(i.emp_id)

            for i in date_list:
                for j in agent_list:
                    emp_obj = Employee.objects.get(emp_id=j)
                    agt_cal = {}
                    try:
                        agt_calendar = EcplCalander.objects.get(date=i, emp_id=j)
                        agt_cal['date'] = i
                        agt_cal['status'] = agt_calendar.att_actual
                        agt_cal['approved_on'] = agt_calendar.approved_on
                        agt_cal['team'] = agt_calendar.team
                        agt_cal['emp_name'] = agt_calendar.emp_name
                        agt_cal['rm1'] = agt_calendar.rm1
                        agt_cal['rm2'] = agt_calendar.rm2
                        agt_cal['rm3'] = agt_calendar.rm3

                    except EcplCalander.DoesNotExist:
                        agt_cal['date'] = i
                        agt_cal['status'] = 'Unmarked'
                        agt_cal['approved_on'] = 'NA'
                        agt_cal['team'] = emp_obj.emp_process
                        agt_cal['emp_name'] = emp_obj.emp_name
                        agt_cal['rm1'] = emp_obj.emp_rm1
                        agt_cal['rm2'] = emp_obj.emp_rm2
                        agt_cal['rm3'] = emp_obj.emp_rm3

                    agt_cal_list.append(agt_cal)

            emp_id = request.user.profile.emp_id
            emp = Employee.objects.get(emp_id=emp_id)

            data = {'agt_cal_list': agt_cal_list,
                    'emp': emp}

            return render(request, 'ams/agent-calander-status.html', data)



        agt_cal_list = []

        agent_list = []
        agents = Employee.objects.filter(emp_process=team_name)
        for i in agents:
            agent_list.append(i.emp_id)

        for i in date_list:
            for j in agent_list:
                emp_obj =Employee.objects.get(emp_id=j)
                agt_cal = {}
                try:
                    agt_calendar = EcplCalander.objects.get(date=i, emp_id=j)
                    agt_cal['date'] = i
                    agt_cal['status'] = agt_calendar.att_actual
                    agt_cal['approved_on'] = agt_calendar.approved_on
                    agt_cal['team'] = agt_calendar.team
                    agt_cal['emp_name'] = agt_calendar.emp_name
                    agt_cal['rm1'] = agt_calendar.rm1
                    agt_cal['rm2'] = agt_calendar.rm2
                    agt_cal['rm3'] = agt_calendar.rm3

                except EcplCalander.DoesNotExist:
                    agt_cal['date'] = i
                    agt_cal['status'] = 'Unmarked'
                    agt_cal['approved_on'] = 'NA'
                    agt_cal['team'] = emp_obj.emp_process
                    agt_cal['emp_name'] = emp_obj.emp_name
                    agt_cal['rm1'] = emp_obj.emp_rm1
                    agt_cal['rm2'] = emp_obj.emp_rm2
                    agt_cal['rm3'] = emp_obj.emp_rm3

                agt_cal_list.append(agt_cal)

        emp_id = request.user.profile.emp_id
        emp = Employee.objects.get(emp_id=emp_id)

        data = {'agt_cal_list': agt_cal_list,
                'emp': emp}

        return render(request, 'ams/agent-calander-status.html', data)

    else:
        return HttpResponse('<h2>*** GET not available ***</h2>')


@login_required
def agentSettings(request):
    emp_id = request.user.profile.emp_id
    emp = Employee.objects.get(emp_id=emp_id)
    form = PasswordChangeForm(request.user)
    data = {'emp':emp,'form':form}
    return render(request,'ams/agent-settings.html',data)

@login_required
def rmSettings(request):
    emp_id = request.user.profile.emp_id
    emp = Employee.objects.get(emp_id=emp_id)
    form = PasswordChangeForm(request.user)
    data = {'emp':emp,'form':form}
    return render(request,'ams/rm-settings.html',data)

@login_required
def uploadImageToDB(request):
    if request.method=='POST':
        user_image = request.FILES['user-img']
        id = request.POST['id']
        prof = Profile.objects.get(id=id)
        prof.img = user_image
        prof.save()

        if request.user.profile.emp_desi in tl_am_list:
            return redirect('/ams/tl-dashboard')
        elif request.user.profile.emp_desi in hr_list:
            return redirect('/ams/hr-dashboard')
        else:
            return redirect('/ams/agent-dashboard')
    else:
        pass

@login_required
def mappingHomePage(request):
    emp_id = request.user.profile.emp_id
    user_nm = request.user.profile.emp_name
    emp = Employee.objects.get(emp_id=emp_id)
    employees = Employee.objects.filter(Q(emp_rm1=user_nm),Q(agent_status = 'Active'))
    rms = Employee.objects.exclude(emp_desi__in=['Client Relationship Officer', 'Patrolling Officer']).order_by(
        'emp_name')
    teams = Campaigns.objects.all()
    data = {'emp': emp,'employees':employees,'rms':rms,'teams':teams}

    return render(request,'ams/mapping_home.html',data)

@login_required
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

@login_required
def viewMappingApplicationStatus(request):
    usr = request.user.profile.emp_name
    tickets = MappingTickets.objects.filter(created_by=usr).order_by('created_date')
    emp_id = request.user.profile.emp_id
    emp = Employee.objects.get(emp_id=emp_id)
    data = {'tickets': tickets, 'emp': emp}
    return render(request, 'ams/view_mapping_status.html', data)



@login_required
def addNewTeam(request):

    mgrs = Employee.objects.filter(emp_desi__in=manager_list,agent_status = 'Active')
    if request.method == "POST":
        usr = request.user.profile.emp_name
        om = request.POST["om"]
        campaign = request.POST["campaign"]
        today = date.today()
        cam = Campaigns.objects.create(name=campaign,om=om,created_by=usr,created_date = today)
        cam.save()
        messages.info(request,'Team ' + campaign +' Created Successfully')

        return redirect('/ams/view-all-teams')

    else:
        emp_id = request.user.profile.emp_id
        emp = Employee.objects.get(emp_id=emp_id)
        data = {'mgrs':mgrs,'emp':emp}
        return render(request,"ams/add_team.html",data)

@login_required
def viewTeam(request):
    if request.user.profile.emp_desi in hr_list:
        teams = Campaigns.objects.all()
        emp_id = request.user.profile.emp_id
        emp = Employee.objects.get(emp_id=emp_id)
        data = {'teams':teams,'emp':emp}
        return render(request,'ams/view_team.html',data)
    else:
        messages.info(request,'*** You are not authorised to view this page ***')
        return redirect('ams/logout')

@login_required
def jobRequisition(request):
    if request.method == "POST":
        log_user = request.user
        req_date = request.POST["req_date"]
        hc_req = request.POST["hc_required"]
        req_raised_by = request.POST["req_rais_by"]
        department = request.POST["department"]
        designation = request.POST["designation"]
        process_typ_one = request.POST["pro_type_1"]
        process_typ_two = request.POST["pro_type_2"]
        process_typ_three = request.POST["pro_type_3"]
        salary_rang_frm = request.POST["sal_from"]
        salary_rang_to = request.POST["sal_to"]
        qualification = request.POST["quali"]
        other_quali = request.POST["other_quali"]
        skills_set = request.POST["skills"]
        languages = request.POST.getlist("lang")
        shift_timing = request.POST["shift"]
        shift_timing_frm = request.POST["shift_from"]
        shift_timing_to = request.POST["shift_to"]
        working_from = request.POST["work_from"]
        working_to = request.POST["work_to"]
        week_no_days = request.POST["num_off"]
        week_from = request.POST.get("off_from")
        week_to = request.POST.get("off_to")
        requisition_typ = request.POST["req_type"]
        e = JobRequisition()
        e.req_date = req_date
        e.hc_req = hc_req
        e.req_raised_by = req_raised_by
        e.department = department
        e.designation = designation
        e.process_typ_one = process_typ_one
        e.process_typ_two = process_typ_two
        e.process_typ_three = process_typ_three
        e.salary_rang_frm = salary_rang_frm
        e.salary_rang_to = salary_rang_to
        e.qualification = qualification
        e.other_quali = other_quali
        e.skills_set = skills_set
        e.languages = languages
        e.shift_timing = shift_timing
        e.shift_timing_frm = shift_timing_frm
        e.shift_timing_to = shift_timing_to
        e.working_from = working_from
        e.working_to = working_to
        e.week_no_days = week_no_days
        if week_from:
            e.week_from = week_from
        if week_to:
            e.week_to = week_to
        e.requisition_typ = requisition_typ
        e.user_name = log_user
        e.save()

        emp_id = request.user.profile.emp_id
        emp = Employee.objects.get(emp_id=emp_id)
        data = {'emp': emp}
        return render(request, "ams/job_requisition.html", data)

    else:
        emp_id = request.user.profile.emp_id
        emp = Employee.objects.get(emp_id=emp_id)
        data = {'emp':emp}
        return render(request, "ams/job_requisition.html",data)

@login_required
def jobRequisitionReportTable(request):
    job = JobRequisition.objects.all()
    emp_id = request.user.profile.emp_id
    emp = Employee.objects.get(emp_id=emp_id)
    data = {'emp':emp,'job':job}
    return render(request, "ams/job_requisition_report_table.html", data)

@login_required
def jobRequisitionReportTableRM(request):

    job = JobRequisition.objects.filter(req_raised_by = request.user.profile.emp_name)
    emp_id = request.user.profile.emp_id
    emp = Employee.objects.get(emp_id=emp_id)
    data = {'emp':emp,'job':job}
    return render(request, "ams/job_requisition_report_table_rm.html", data)

@login_required
def viewJobEditRequisition(request):
    if request.method == 'POST':
        rowid = request.POST.get("rowid")
        job = JobRequisition.objects.get(id=rowid)
        emp_id = request.user.profile.emp_id
        emp = Employee.objects.get(emp_id=emp_id)
        data = {'emp':emp,'job':job}
        return render(request, "ams/job_requisition_edit.html", data)
    else:
        return HttpResponse('<h1>No Get method Available</h1>')

@login_required
def updateJobForm(request,id):

    if request.method == 'POST':
        log_user = request.user
        job = JobRequisition.objects.get(id=id)
        candidate_name = request.POST["cand_name"]
        closure_date = request.POST["clos_date"]
        source = request.POST["source"]
        source_empref_emp_name = request.POST["emp_name"]
        source_empref_emp_id = request.POST["emp_id"]
        source_social = request.POST.get('social')
        source_partners = request.POST.get("partner")
        recruited_people = request.POST["rec_peo"]
        request_status = request.POST.get("req_status")
        candidate_remark = request.POST["can_remark"]

        job.candidate_remark = candidate_remark
        job.candidate_name = candidate_name
        job.closure_date = closure_date
        job.source = source
        job.source_empref_emp_name = source_empref_emp_name
        job.source_empref_emp_id = source_empref_emp_id
        job.source_social = source_social
        job.source_partners = source_partners
        job.recruited_people = recruited_people
        job.user_name = log_user
        if request_status:
            job.request_status = request_status
        if request_status == "Completed":
            job.status = True
        job.save()

        return redirect("/ams/view-job-table")
    else:
        job = JobRequisition.objects.get(id=id)
        emp_id = request.user.profile.emp_id
        emp = Employee.objects.get(emp_id=emp_id)
        data = {'job':job,'emp':emp}
        return render(request, "ams/job_requisition_edit.html", data)

@login_required
def applyLeave(request):

    if request.method == 'POST':
        emp_name = request.POST["emp_name"]
        emp_id = request.POST["emp_id"]
        emp_desi = request.POST["emp_desi"]
        emp_process = request.POST["emp_process"]
        emp_rm1 = request.POST["emp_rm1"]
        emp_rm2 = request.POST["emp_rm2"]
        emp_rm3 = request.POST["emp_rm3"]
        leave_type = request.POST["type"]
        start_date = request.POST["startdate"]
        end_date = request.POST["enddate"]
        no_days = request.POST["leave_days"]
        agent_reason = request.POST["reason"]


        e = LeaveTable()
        e.applied_date = date.today()
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

        if emp_desi in manager_list or emp_desi in tl_am_list:
            e.tl_status = 'Approved'
            e.tl_approval = True
            e.tl_reason = 'Self Approved'

        e.save()



        leave_balance = EmployeeLeaveBalance.objects.get(emp_id=emp_id)

        if leave_type == 'PL':
            leave_balance.pl_balance-=int(no_days)
            leave_balance.save()
        elif leave_type == 'SL':
            leave_balance.sl_balance-=int(no_days)
            leave_balance.save()

        return redirect('/ams/ams-apply_leave')

    else:

        emp_id = request.user.profile.emp_id
        emp = Employee.objects.get(emp_id=emp_id)
        leave = LeaveTable.objects.filter(emp_id=emp_id)

        try:
            leave_balance = EmployeeLeaveBalance.objects.get(emp_id=emp_id)
        except EmployeeLeaveBalance.DoesNotExist:
            leave_balance = {'sl_balance':0,'pl_balance':0}

        data = {'emp': emp,'leave':leave,'leave_balance':leave_balance}
        return render(request,'ams/apply-leave.html',data)

@login_required
def viewleaveListRM1(request):

    emp_id = request.user.profile.emp_id
    emp = Employee.objects.get(emp_id=emp_id)
    leave_request = LeaveTable.objects.filter(emp_rm1=request.user.profile.emp_name,tl_approval=False)
    data = {'emp':emp,'leave_request':leave_request}
    return render(request,'ams/leave_approval_rm1.html',data)

@login_required
def approveLeaveRM1(request):

    if request.method == "POST":
        id = request.POST["id"]
        e = LeaveTable.objects.get(id=id)
        emp_id = e.emp_id
        leave_type = e.leave_type
        no_days = e.no_days

        tl_response = request.POST['tl_response']
        tl_reason = request.POST['tl_reason']

        if tl_response == 'Approve':
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

        e.tl_approval = tl_approval
        e.tl_reason = tl_reason
        e.tl_status = tl_status
        e.status = status
        e.save()

        return redirect('/ams/view-leave-list')


@login_required
def editAgentStatus(request):
    if request.method == 'POST':

        id = request.POST['id']
        agent_status = request.POST['new_status']
        reason = request.POST['reason']
        profile = Profile.objects.get(id=id)
        emp = Employee.objects.get(emp_id = profile.emp_id)
        emp.agent_status = agent_status
        emp.save()
        profile.agent_status = agent_status
        profile.save()
        sh = AgentActiveStatusHist.objects.create(emp_id = profile.emp_id,emp_name=profile.emp_name ,current_status = profile.agent_status,
                                                  new_status= agent_status,
                                                  date=date.today() ,reason =reason ,changed_by =request.user.profile.emp_name)

        sh.save()
        return redirect('/ams/viewusers')

    else:
        return HttpResponse('<h1>Not Get Method</h1>')

@login_required
def viewAttrition(request):
    emp_idd = request.user.profile.emp_id
    emp = Employee.objects.get(emp_id=emp_idd)

    if request.method == 'POST':

        emp_id = request.POST['emp_id']
        try:
            prof = Profile.objects.get(emp_id = emp_id)
            prof.agent_status = 'Attrition'
            prof.save()

        except Profile.DoesNotExist:
            messages.info(request,'Incorrect Employee Id, Please contact Admin')
            att = EcplCalander.objects.filter(att_actual='Attrition').distinct()

            data = {'att': att,'emp':emp}
            return render(request, 'ams/view_attrition.html', data)

        try:
            prof = Employee.objects.get(emp_id = emp_id)
            prof.agent_status = 'Attrition'
            prof.save()

        except Employee.DoesNotExist:
            messages.info(request,'Incorrect Employee Id, Please contact Admin')
            att = EcplCalander.objects.filter(att_actual='Attrition').distinct()

            data = {'att': att,'emp':emp}
            return render(request, 'ams/view_attrition.html', data)

        cal = EcplCalander.objects.filter(emp_id=emp_id,att_actual='Attrition')
        for i in cal:
            i.att_actual = 'Attrition - approved'
            i.save()


        att = EcplCalander.objects.filter(att_actual='Attrition').distinct()
        data = {'att': att,'emp':emp}
        return render(request, 'ams/view_attrition.html', data)

    else:
        att = EcplCalander.objects.filter(att_actual = 'Attrition').distinct()

        data = {'att':att,'emp':emp}
        return render(request,'ams/view_attrition.html',data)

def attendanceCorrection(request):

    emp_name = request.user.profile.emp_name
    emp_idd = request.user.profile.emp_id
    emp = Employee.objects.get(emp_id=emp_idd)

    if request.method == 'POST':
        date = request.POST['date']
        emp_id = request.POST['emp_id']

        emp_obj = Employee.objects.get(emp_id = emp_id)

        try:
            cal = EcplCalander.objects.get(date = date,emp_id = emp_id)

        except EcplCalander.DoesNotExist:
            cal = {'date':date,'emp_name':emp_obj.emp_name,'emp_id':emp_id,'team':emp_obj.emp_process,'att_actual':'Unmarked'}

        atthist = AttendanceCorrectionHistory.objects.filter(applied_by_id = emp_idd)
        data = {'cal':cal,'emp':emp,'atthist':atthist}

        return render(request,'ams/view_att_correction_apply.html',data)

    else:

        all_emp = Employee.objects.filter(Q(agent_status='Active'),
                                          Q(emp_rm1=emp_name) | Q(emp_rm2=emp_name) | Q(emp_rm3=emp_name))

        atthist = AttendanceCorrectionHistory.objects.filter(applied_by_id=emp_idd)
        data = {'all_emp':all_emp,'emp':emp,'atthist':atthist}

        return render(request,'ams/view_att_correction.html',data)

def applyCorrection(request):

    applied_by = request.user.profile.emp_name
    applied_by_id = request.user.profile.emp_id

    if request.method == 'POST':

        id = request.POST['id']
        att_new = request.POST['att_new']
        att_old = request.POST['att_old']
        date = request.POST['date']
        emp_id = request.POST['emp_id']
        emp_obj = Employee.objects.get(emp_id=emp_id)

        if att_old == 'Unmarked':

            cal = EcplCalander()
            cal.team = emp_obj.emp_process
            cal.date = date
            cal.emp_name = emp_obj.emp_name
            cal.emp_id = emp_id
            cal.emp_desi = emp_obj.emp_desi
            cal.att_actual = att_new
            cal.approved_on = datetime.today()
            cal.appoved_by =applied_by
            cal.applied_status = True
            cal.rm1 = emp_obj.emp_rm1
            cal.rm2 = emp_obj.emp_rm2
            cal.rm3 = emp_obj.emp_rm3

            cal.save()

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
            atthist.cal_id = cal.id
            atthist.save()

            messages.info(request, 'Attendance Correction Request has been sent Successfully')
            return redirect('/ams/attendance-correction')


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
        atthist.cal_id = id
        atthist.save()

        messages.info(request,'Attendance Correction Request has been sent Successfully')
        return redirect('/ams/attendance-correction')

    else:
        pass


def approveAttendanceRequest(request):

    emp_idd = request.user.profile.emp_id
    emp = Employee.objects.get(emp_id=emp_idd)

    if request.method == 'POST':

        id = request.POST['id']
        cal_id = request.POST['cal_id']
        hr_resp = request.POST['hr_resp']
        comments = request.POST['comments']

        hist = AttendanceCorrectionHistory.objects.get(id=id)
        cal = EcplCalander.objects.get(id=cal_id)
        cal.att_actual = hist.att_new

        cal.save()
        hist.status = True
        hist.comments =comments
        hist.approved_by = request.user.profile.emp_name
        hist.hr_response = hr_resp

        hist.save()

        return redirect('/ams/approve-att-correction-req')

        pass
    else:

        att_hist = AttendanceCorrectionHistory.objects.filter(status = False)

        data = {'att_hist':att_hist,'emp':emp}

        return render(request,'ams/hr_attendance_correction.html',data)