import datetime
import math
import random
from datetime import date
import socket
import pytz
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.core.mail import EmailMessage
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.template.loader import get_template
from .models import *
from django.apps import apps

Profile = apps.get_model('mapping', 'Profile')
Campaigns = apps.get_model('ams', 'Campaigns')
AllAgents = apps.get_model('mapping', 'Profile')

# For HTML Scripts
number = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
# Login
hr_list = ['HR', 'HR Manager', 'Manager ER', 'HR Lead', 'Sr Recruiter', 'MIS Executive HR', 'Lead HRBP',
           'Employee Relations Specialist', 'Payroll Specialist', 'Recruiter', 'HR Generalist', 'Associate Director',
           'Junior Recruiter']

am_mgr_list = ['Assistant Manager', 'Learning and Development Head', 'Quality Head', 'Operations Manager',
               'Service Delivery Manager', 'Command Centre Head', 'Manager']
# Edit/Update
edit_list = ['HR', 'HR Manager', 'Manager ER', 'HR Lead',
             'Sr Recruiter', 'MIS Executive HR', 'Lead HRBP', 'Employee Relations Specialist', 'Payroll Specialist',
             'Recruiter', 'Junior Recruiter', 'HR Generalist']

# Frontend filtering managers
mgr_list = ['Learning and Development Head', 'Quality Head', 'Operations Manager', 'Service Delivery Manager',
            'Command Centre Head', 'Manager']


# Frontend export option
management_list = ['Associate Director']

@login_required
def Index(request):
    return redirect('/ams/dashboard-redirect')

@login_required
def Login(request):
    username = request.user.profile.emp_id
    user = Profile.objects.get(emp_id=username)
    system = socket.gethostname()
    IPAddr = socket.gethostbyname(system)
    date_time = datetime.datetime.now()
    emp_id = request.user.profile.emp_id
    emp_name = request.user.profile.emp_name
    e = LoginHistory()
    e.emp_id = emp_id
    e.emp_name = emp_name
    e.date_time = date_time
    e.ip = IPAddr
    e.system = system
    e.save()
    designation = request.user.profile.emp_desi

    if user.emp_email is not None and user.email_verify == True:
        if designation in am_mgr_list:
            return redirect("/erf/manager-dashboard")
        elif designation in hr_list:
            return redirect("/erf/hr-dashboard")
        else:
            messages.info(request, 'Not authorised to view this page !')
            return redirect("/erf/")
    else:
        return redirect("/erf/add-email")

@login_required
def AddEmail(request):
    designation = request.user.profile.emp_desi
    if request.method == "POST":
        emp_id = request.POST["emp_id"]
        email = request.POST["email"]
        profile = Profile.objects.all()
        digits = "0123456789"
        OTP = ""
        for i in range(6):
            OTP += digits[math.floor(random.random() * 10)]
        try:
            Profile.objects.get(emp_id=emp_id,emp_email=email)
            messages.info(request,"OTP is sent to your email ID Entered. Please Verify it. Avoid Clicking multiple times.")
            return redirect("/erf/verify-email")
        except Profile.DoesNotExist:
            for i in profile:
                if i.emp_email == email:
                    m = "The Email ID Entered is already in use by someone else. Please use another Email."
                    messages.info(request, m)
                    return redirect("/erf/add-email")
            e = Profile.objects.get(emp_id=emp_id)
            e.emp_email = email
            e.otp = OTP
            e.otp_time = datetime.datetime.now()
            e.save()
            subject = "Your OTP for ERF"
            email_template = "Your OTP for ERF is <b>" + str(OTP) + "</b> Valid only for 5 Minutes.<br><br>"
            to = [email]
            email_msg = EmailMessage(subject,
                                     email_template, 'erf@expertcallers.com',
                                     to,
                                     reply_to=['erf@expertcallers.com'])
            email_msg.content_subtype = 'html'
            email_msg.send(fail_silently=False)
            messages.info(request, "OTP is sent to your email ID Entered. Please Verify it.")
            return redirect("/erf/verify-email")
    else:
        messages.info(request, 'Please add your Email ID')
        return render(request, "erf/add-email.html")

@login_required
def VerifyEmail(request):
    designation = request.user.profile.emp_desi
    emp_id = request.user.profile.emp_id
    e = Profile.objects.get(emp_id=emp_id)
    if request.method == "POST":
        start = e.otp_time.timestamp()
        timee = datetime.datetime.now(pytz.timezone('Asia/Kolkata')).timestamp() - start
        if timee <= 300:
            otp = request.POST["otp"]
            if e.otp == otp:
                e.email_verify = True
                e.save()
                messages.info(request, "Email Verified Successfully!")
                if designation in am_mgr_list:
                    return redirect("/erf/manager-dashboard")
                elif designation in hr_list:
                    return redirect("/erf/hr-dashboard")
                else:
                    messages.info(request, 'Not authorised to view this page !')
                    return redirect("/erf/")
            else:
                messages.info(request, "Invalid OTP please enter Correct OTP")
                return redirect("/erf/verify-email")
        else:
            messages.info(request, "The OTP has expired. New OTP is sent, please enter New OTP!")
            digits = "0123456789"
            OTP = ""
            for i in range(6):
                OTP += digits[math.floor(random.random() * 10)]
            e = Profile.objects.get(emp_id=emp_id)
            e.otp = OTP
            e.otp_time = datetime.datetime.now()
            e.save()
            subject = "Your OTP for ERF"
            email_template = "Your OTP for ERF is <b>" + str(OTP) + "</b> Valid only for 5 Minutes.<br><br>"
            to = [request.user.profile.emp_email]
            email_msg = EmailMessage(subject,
                                     email_template, 'erf@expertcallers.com',
                                     to,
                                     reply_to=['erf@expertcallers.com'])
            email_msg.content_subtype = 'html'
            email_msg.send(fail_silently=False)
            return redirect("/erf/verify-email")
    else:
        data = {"profile":e}
        return render(request, "erf/verify-email.html",data)


@login_required
def EditEmail(request):
    user = request.user.profile
    if request.method == "POST":
        emp_id = request.POST["emp_id"]
        email = request.POST["new_email"]
        if user.emp_email == email:
            m = "The New Email is same as Previous Email, hence Email not changed :)"
            messages.info(request,m)
            return redirect("/erf/settings")
        else:
            digits = "0123456789"
            OTP = ""
            for i in range(6):
                OTP += digits[math.floor(random.random() * 10)]
            try:
                Profile.objects.get(emp_id=emp_id,emp_email=email)
                m = "OTP is sent to your email ID Entered. Please Verify it. Avoid Clicking multiple times."
                messages.info(request,m)
                return redirect("/erf/verify-email")
            except Profile.DoesNotExist:
                e = Profile.objects.get(emp_id=emp_id)
                e.emp_email = email
                e.otp = OTP
                e.email_verify = False
                e.otp_time = datetime.datetime.now()
                e.save()
                subject = "Your OTP for ERF"
                email_template = "Your OTP for ERF is <b>" + str(OTP) + "</b> Valid only for 5 Minutes.<br><br>"
                to = [email]
                email_msg = EmailMessage(subject,
                                         email_template, 'erf@expertcallers.com',
                                         to,
                                         reply_to=['erf@expertcallers.com'])
                email_msg.content_subtype = 'html'
                email_msg.send(fail_silently=False)
                messages.info(request, "OTP is sent to your email ID Entered. Please Verify it.")
                return redirect("/erf/verify-email")
    else:
        messages.info(request, "Invalid Request. You have been logged out :)")
        return redirect("/erf/")

def forgotPassword(request):
    if request.method == "POST":
        emp_id = request.POST["emp_id"]
        try:
            profile = Profile.objects.get(emp_id=emp_id)
            email = profile.emp_email
            if email is not None:
                digits = "0123456789"
                OTP = ""
                for i in range(6):
                    OTP += digits[math.floor(random.random() * 10)]
                try:
                    Profile.objects.get(emp_id=emp_id,otp=OTP)
                    m = "Link to reset the password is sent to your email. (" + email + ") Please check your mail " \
                        "and reset it from there. Avoid Clicking Multiple Times :)"
                    messages.info(request, m)
                    return redirect("/erf/")
                except Profile.DoesNotExist:
                    profile.otp = OTP
                    profile.otp_time = datetime.datetime.now()
                    profile.save()
                    subject = "Password Reset Link of ERF"
                    email_template = "Click on the link Below to reset your password. Remember it is valid only for " \
                                     "5 Min<br><br><a href='http://dashboard.ecpl/erf/reset-password/"+emp_id+"/"+OTP+"'>" \
                                     "http://dashboard.ecpl/erf/reset-password/"+emp_id+"/"+OTP+"</a><br><br>"
                    to = [email]
                    email_msg = EmailMessage(subject,
                                             email_template, 'erf@expertcallers.com',
                                             to,
                                             reply_to=['erf@expertcallers.com'])
                    email_msg.content_subtype = 'html'
                    email_msg.send(fail_silently=False)
                    m = "Link to reset the password is sent to your email. ("+email+") Please check your mail " \
                                                                                    "and reset it from there."
                    messages.info(request, m)
                    return redirect("/erf/")
            else:
                m = "Could not find your email. Please Enter Username and Password as your Emp ID: " \
                    ""+emp_id+" and try to login again"
                messages.info(request, m)
                return redirect("/erf/")

        except Profile.DoesNotExist:
            messages.info(request,"Invalid Username! Enter Correct Username")
            return redirect("/erf/forgot-password")
    else:
        return render(request, "erf/forgot_password.html")

def resetPassword(request,emp_id,otp):
    profile = Profile.objects.get(emp_id=emp_id)
    start = profile.otp_time.timestamp()
    timee = datetime.datetime.now(pytz.timezone('Asia/Kolkata')).timestamp() - start
    if request.method == "POST":
        user = User.objects.get(username=emp_id)
        new_pass = request.POST["npass"]
        c_pass = request.POST["cpass"]
        if new_pass == c_pass:
            user.password = make_password(new_pass)
            user.save()
            messages.info(request, "The Password has been reset Successfully. Login with new Password.")
            return redirect("/erf/")
        else:
            messages.info(request, "The Passwords does not match. Please fill again ")
            return redirect("/erf/reset-password/"+emp_id+"/"+otp)
    else:
        if timee <= 300:
            if profile.otp == otp and profile.emp_id == emp_id:
                return render(request, "erf/reset_password.html")
            else:
                messages.info(request, "Invalid Link :)")
                return redirect("/erf/")
        else:
            messages.info(request, "The Link has expired. New Link is sent, Please check your email")
            digits = "0123456789"
            OTP = ""
            for i in range(6):
                OTP += digits[math.floor(random.random() * 10)]
            profile.otp = OTP
            profile.otp_time = datetime.datetime.now()
            profile.save()
            subject = "Password Reset Link of ERF"
            email_template = "Click on the link Below to reset your password. Remember it is valid only for " \
                             "5 Min<br><br><a href='http://127.0.0.1:8000/erf/reset-password/" + emp_id + "/" + OTP + "'>" \
                             "http://127.0.0.1:8000/erf/reset-password</a><br><br>"
            to = [profile.emp_email]
            email_msg = EmailMessage(subject,
                                     email_template, 'erf@expertcallers.com',
                                     to,
                                     reply_to=['erf@expertcallers.com'])
            email_msg.content_subtype = 'html'
            email_msg.send(fail_silently=False)
            return redirect("/erf/")


@login_required
def dashboardRedirects(request):
    designation = request.user.profile.emp_desi
    if designation in am_mgr_list:
        return redirect("/erf/manager-dashboard")
    elif designation in hr_list:
        return redirect("/erf/hr-dashboard")
    else:
        messages.info(request, 'Not authorised to view this page !')
        return redirect("/erf/")


@login_required
def ManagerDashboard(request):
    designation = request.user.profile.emp_desi
    emp_id = request.user.profile.emp_id
    if designation in am_mgr_list:
        all = JobRequisition.objects.filter(Q(created_by_id=emp_id) | Q(created_by_rm1_id=emp_id) | Q(created_by_manager_id=emp_id), manager_approval=True, ticket_status=True).count()
        open = JobRequisition.objects.filter(Q(created_by_id=emp_id) | Q(created_by_rm1_id=emp_id) | Q(created_by_manager_id=emp_id), final_status=False, manager_approval=True, ticket_status=True).count()
        closed = JobRequisition.objects.filter(Q(created_by_id=emp_id) | Q(created_by_rm1_id=emp_id) | Q(created_by_manager_id=emp_id), final_status=True, manager_approval=True, ticket_status=True).count()
        dead_line = JobRequisition.objects.filter(Q(created_by_id=emp_id) | Q(created_by_rm1_id=emp_id) | Q(created_by_manager_id=emp_id), final_status=False, manager_approval=True, ticket_status=True)
        today = datetime.date.today()
        dead_line_count_list = []
        for i in dead_line:
            if i.dead_line < today:
                dead_line_count_list.append(i.id)
        dead_line_count = len(dead_line_count_list)
        approval = JobRequisition.objects.filter(created_by_manager_id=emp_id, initial_status=True,
                                                 final_status=False, manager_approval=True, ticket_status=True).count()

        manager_approval = JobRequisition.objects.filter(created_by_rm1_id=emp_id, manager_approval=False, ticket_status=False).count()

        waiting = JobRequisition.objects.filter(created_by_id=emp_id, manager_approval=False, ticket_status=False).count()

        data = {"all": all, "open": open, "closed": closed, "dead_line": dead_line_count, "approval": approval,
                "manager": mgr_list,"manager_approval":manager_approval,"waiting":waiting}
        return render(request, "erf/manager_dashboard.html", data)
    else:
        messages.info(request, "Invalid Request. You have been logged out :)")
        return redirect("/erf/")


@login_required
def HRDashboard(request):
    designation = request.user.profile.emp_desi
    usr = request.user
    if designation in hr_list:
        manager = Profile.objects.all()
        all = JobRequisition.objects.filter(manager_approval=True, ticket_status=True).count()
        open = JobRequisition.objects.filter(initial_status=False, manager_approval=True, ticket_status=True).count()
        closed = JobRequisition.objects.filter(final_status=True, manager_approval=True, ticket_status=True).count()
        added = JobRequisition.objects.filter(created_by_id=usr, manager_approval=True, ticket_status=True).count()
        waiting = JobRequisition.objects.filter(initial_status=True, final_status=False, manager_approval=True, ticket_status=True).count()
        dead_line = JobRequisition.objects.filter(final_status=False, manager_approval=True, ticket_status=True)
        deletion = JobRequisition.objects.filter(deletion=True, ticket_status=True).count()
        today = datetime.date.today()
        dead_line_count_list = []
        for i in dead_line:
            if i.dead_line < today:
                dead_line_count_list.append(i.id)
        dead_line_count = len(dead_line_count_list)
        data = {"all": all, "open": open, "closed": closed, "added": added, "manager": manager, "waiting": waiting,
                "dead_line": dead_line_count,"management":management_list,"deletion":deletion}
        return render(request, "erf/hr_dashboard.html", data)
    else:
        messages.info(request, "Invalid Request. You have been logged out :)")
        return redirect("/erf/")


@login_required
def job_requisition(request):
    user = request.user.profile
    if request.method == "POST":
        requisition_date = datetime.datetime.now(pytz.timezone('Asia/Kolkata'))
        weekday = datetime.datetime.now(pytz.timezone('Asia/Kolkata')).weekday()
        time = datetime.datetime.now(pytz.timezone('Asia/Kolkata')).time()
        today7pm = time.replace(hour=19, minute=0, second=0, microsecond=0)
        new_weekday = datetime.datetime.now(pytz.timezone('Asia/Kolkata')).weekday()
        edited_date = datetime.datetime.now()
        if weekday < 5:
            if time > today7pm:
                edited_date = (datetime.datetime.today() + datetime.timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0)
                new_weekday = edited_date.weekday()
        if new_weekday == 5:
            edited_date = (datetime.datetime.today() + datetime.timedelta(days=2)).replace(hour=9, minute=0, second=0, microsecond=0)
        elif new_weekday == 6:
            edited_date = (datetime.datetime.today() + datetime.timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0)
        else:
            edited_date = edited_date
        hc_req = request.POST["hc_required"]
        req_raised_by = request.POST["req_rais_by"]
        created_by_id = request.user.profile.emp_id
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
        type_of_working = request.POST["working_days"]
        working_from = request.POST.get("work_from")
        working_to = request.POST.get("work_to")
        week_no_days = request.POST.get("num_off")
        week_from = request.POST.get("off_from")
        week_to = request.POST.get("off_to")
        requisition_typ = request.POST["req_type"]
        replace_reason = request.POST["replace_reason"]
        manager_id = request.POST["manager"]
        manager = Profile.objects.get(emp_id=manager_id).emp_name
        campaign = request.POST["campaign"]
        pricing = request.POST["pricing"]
        unique_id = request.POST["csrfmiddlewaretoken"]


        dead_line = int(request.POST["dead_line"])
        new_edited_date = edited_date
        dead_line = new_edited_date + datetime.timedelta(days=dead_line)
        while new_edited_date <= dead_line:
            a = new_edited_date.weekday()
            if a == 5 or a == 6:
                dead_line += datetime.timedelta(days=1)
            new_edited_date += datetime.timedelta(days=1)
        new_campaign = request.POST.get("new_campaign")
        if new_campaign:
            try:
                c = Campaigns.objects.get(name__iexact=new_campaign)
                campaign = c.name
                messages.info(request, "Campaign Not added! Campaign with same name already exist!!")
            except Campaigns.DoesNotExist:
                cam = Campaigns()
                cam.name = new_campaign
                cam.created_by = "Created while adding Request by "+ str(request.user.profile.emp_id)
                cam.save()
                campaign = new_campaign

        try:
            JobRequisition.objects.get(unique_id=unique_id)
            messages.info(request, "Request added please wait!")
            return redirect("/erf/dashboard")

        except JobRequisition.DoesNotExist:
            e = JobRequisition()
            if user.emp_desi != "Assistant Manager":
                e.manager_approval = True
            else:
                e.request_status = "Waiting for Manager to Approve"
                e.ticket_status = False
            e.created_by_rm1 = user.emp_rm1
            e.created_by_rm1_id = user.emp_rm1_id
            e.campaign = campaign
            e.pricing = pricing
            e.edited_date = edited_date
            e.unique_id = unique_id
            e.dead_line = dead_line
            e.type_of_working = type_of_working
            e.requisition_date = requisition_date
            e.hc_req = hc_req
            e.req_raised_by = req_raised_by
            e.created_by_manager = manager
            e.created_by_manager_id = manager_id
            e.department = department
            e.designation = designation
            e.process_type_one = process_typ_one
            e.process_type_two = process_typ_two
            e.process_type_three = process_typ_three
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
            if week_no_days:
                e.week_no_days = week_no_days
            if week_from:
                e.week_from = week_from
            if week_to:
                e.week_to = week_to
            e.requisition_type = requisition_typ
            e.reason_for_replace = replace_reason
            e.created_by_id = created_by_id
            e.save()

            a = Tickets()
            a.job_requisition_id = e.id
            a.created_by = req_raised_by
            a.created_by_id = created_by_id
            a.created_date = edited_date
            now_datetime = datetime.datetime.now().strftime('%b %d,%Y %H:%M:%S')
            a.edited_by = [now_datetime, req_raised_by, created_by_id, "Created"]
            a.save()
            edit = JobRequisition.objects.get(id=e.id)
            edit.ticket_id = a
            edit.save()
            messages.info(request, "Employee Requisition Added Successfully !!")
            if user.emp_desi != "Assistant Manager":
                action = "Created"
                subject = action + " - Employee Requisition [" + str(e.id) + "]"
                html_path = 'erf/email.html'
                data = {'id': e.id, "created_date": edited_date, "hc": hc_req, "department": department,
                        "position": designation,
                        "deadline": dead_line, "campaign": campaign, "user": user.emp_name, "action": action,
                        "status": "Pending"}
                email_template = get_template(html_path).render(data)
                manager_email = Profile.objects.get(emp_id=manager_id).emp_email
                try:
                    rm1_email = Profile.objects.get(emp_id=user.emp_rm1_id).emp_email
                except Profile.DoesNotExist:
                    rm1_email = request.user.profile.emp_email
                to = [request.user.profile.emp_email, rm1_email]
                email_msg = EmailMessage(subject,
                                         email_template, 'erf@expertcallers.com',
                                         to,
                                         reply_to=['erf@expertcallers.com'])
                email_msg.content_subtype = 'html'
                email_msg.send(fail_silently=False)
            else:
                action = "Created"
                subject = action + " - Employee Requisition [" + str(e.id) +"]"
                html_path = 'erf/email.html'
                data = {'id': e.id, "created_date": edited_date, "hc": hc_req, "department": department,
                        "position": designation,
                        "deadline": dead_line, "campaign": campaign, "user": user.emp_name, "action": action,
                        "status": "Pending"}
                email_template = get_template(html_path).render(data)
                manager_email = Profile.objects.get(emp_id=manager_id).emp_email
                try:
                    rm1_email = Profile.objects.get(emp_id=user.emp_rm1_id).emp_email
                except Profile.DoesNotExist:
                    rm1_email = request.user.profile.emp_email
                to = [request.user.profile.emp_email, "ta@expertcallers.com","dina@expertcallers.com","joseph@expertcallers.com", manager_email, rm1_email]
                email_msg = EmailMessage(subject,
                                         email_template, 'erf@expertcallers.com',
                                         to,
                                         reply_to=['erf@expertcallers.com'])
                email_msg.content_subtype = 'html'
                email_msg.send(fail_silently=False)
            return redirect("/erf/dashboard")

    else:
        managers = Profile.objects.filter(emp_desi__in=mgr_list)
        today = date.today()
        campaigns = Campaigns.objects.all()
        data = {"today": today, "managers": managers, "campaigns": campaigns}
        return render(request, "erf/job_requisition.html", data)


@login_required
def jobRequisitionOpen(request):
    designation = request.user.profile.emp_desi
    if designation in hr_list:
        job = JobRequisition.objects.filter(initial_status=False, manager_approval=True, ticket_status=True)
        data = {"job": job, "number": number, "type": "open", 'desi': 'hr', "editaccess": edit_list}
        return render(request, "erf/job_requisition_table.html", data)
    else:
        messages.info(request, "Invalid Request. You have been logged out :)")
        return redirect("/erf/")


@login_required
def jobRequisitionSelf(request, type):
    user = request.user.profile.emp_id
    if type == "all":
        job = JobRequisition.objects.filter(Q(created_by_id=user) | Q(created_by_rm1_id=user) | Q(created_by_manager_id=user), manager_approval=True, ticket_status=True)
        data = {"job": job, "type": type, "number": number, "editaccess": edit_list}
        return render(request, "erf/job_requisition_table.html", data)
    elif type == "open":
        job = JobRequisition.objects.filter(Q(created_by_id=user) | Q(created_by_rm1_id=user) | Q(created_by_manager_id=user), final_status=False, manager_approval=True, ticket_status=True)
        data = {"job": job, "type": type, "number": number, "editaccess": edit_list}
        return render(request, "erf/job_requisition_table.html", data)
    elif type == "closed":
        job = JobRequisition.objects.filter(Q(created_by_id=user) | Q(created_by_rm1_id=user) | Q(created_by_manager_id=user), final_status=True, manager_approval=True, ticket_status=True)
        data = {"job": job, "type": type, "number": number, "editaccess": edit_list}
        return render(request, "erf/job_requisition_table.html", data)
    elif type == "dead-line":
        today = datetime.date.today()
        job = JobRequisition.objects.filter(Q(created_by_id=user) | Q(created_by_rm1_id=user) | Q(created_by_manager_id=user), final_status=False, manager_approval=True, ticket_status=True)
        job_list = []
        for i in job:
            if i.dead_line < today:
                job_list.append(i)
        data = {"job": job_list, "type": type, "number": number, "editaccess": edit_list}
        return render(request, "erf/job_requisition_table.html", data)
    elif type == "approval":
        job = JobRequisition.objects.filter(created_by_manager_id=user, initial_status=True, final_status=False, ticket_status=True)
        data = {"job": job, "type": type, "number": number, "editaccess": edit_list, "manager": mgr_list}
        return render(request, "erf/job_requisition_table.html", data)
    elif type == "range":
        if request.method == "POST":
            status = request.POST["status"]
            start = request.POST["start_date"]
            tomorrow = str(datetime.date.today() + datetime.timedelta(days=1))
            end = request.POST.get("end_date")
            if end:
                end = datetime.datetime.strptime(end, "%Y-%m-%d")
            else:
                end = datetime.datetime.strptime(tomorrow, "%Y-%m-%d")
            end = end + datetime.timedelta(days=1)
            if status == "all":
                job = JobRequisition.objects.filter(Q(created_by_id=user) | Q(created_by_rm1_id=user) | Q(created_by_manager_id=user), ticket_status=True, edited_date__range=[start, end])
            elif status == "open":
                job = JobRequisition.objects.filter(Q(created_by_id=user) | Q(created_by_rm1_id=user) | Q(created_by_manager_id=user), ticket_status=True, final_status=False,
                                                    edited_date__range=[start, end])
            elif status == "closed":
                job = JobRequisition.objects.filter(Q(created_by_id=user) | Q(created_by_rm1_id=user) | Q(created_by_manager_id=user), ticket_status=True, final_status=True,
                                                    edited_date__range=[start, end])
            else:
                pass
            data = {"job": job, "type": type, "number": number, "editaccess": edit_list}
            return render(request, "erf/job_requisition_table.html", data)
        else:
            messages.info(request, "Invalid Request. You have been logged out :)")
            return redirect("/erf/")
    elif type == "initial":
        job = JobRequisition.objects.filter(created_by_rm1_id=user, ticket_status=False, manager_approval=False)
        data = {"job": job, "type": type, "number": number, "editaccess": edit_list, "manager": mgr_list}
        return render(request, "erf/job_requisition_table.html", data)
    elif type == 'waiting':
        job = JobRequisition.objects.filter(created_by_id=user, manager_approval=False, ticket_status=False)
        data = {"job": job, "type": type, "number": number, "editaccess": edit_list, "manager": mgr_list}
        return render(request, "erf/job_requisition_table.html", data)
    else:
        messages.info(request, "Invalid Request. You have been logged out :)")
        return redirect("/erf/")


@login_required
def jobRequisitionAll(request, type):
    if type == "all":
        job = JobRequisition.objects.filter(manager_approval=True, ticket_status=True)
        data = {"job": job, "type": type, "number": number, "editaccess": edit_list}
        return render(request, "erf/job_requisition_table.html", data)
    if type == "closed":
        job = JobRequisition.objects.filter(final_status=True, manager_approval=True, ticket_status=True)
        data = {"job": job, "type": type, "number": number, "editaccess": edit_list}
        return render(request, "erf/job_requisition_table.html", data)
    elif type == "waiting":
        job = JobRequisition.objects.filter(initial_status=True, final_status=False, manager_approval=True, ticket_status=True)
        data = {"job": job, "type": type, "number": number, "editaccess": edit_list}
        return render(request, "erf/job_requisition_table.html", data)
    elif type == "range":
        if request.method == "POST":
            manager = request.POST["manager"]
            status = request.POST["status"]
            start = request.POST["start_date"]
            tomorrow = str(datetime.date.today() + datetime.timedelta(days=1))
            end = request.POST.get("end_date")
            if end:
                end = datetime.datetime.strptime(end, "%Y-%m-%d")
            else:
                end = datetime.datetime.strptime(tomorrow, "%Y-%m-%d")
            end = end + datetime.timedelta(days=1)
            if manager == "all" and status == "all":
                job = JobRequisition.objects.filter(edited_date__range=[start, end])
            elif manager == "all" and status == "open":
                job = JobRequisition.objects.filter(final_status=False, ticket_status=True, edited_date__range=[start, end])
            elif manager == "all" and status == "closed":
                job = JobRequisition.objects.filter(final_status=True, ticket_status=True, edited_date__range=[start, end])
            elif manager != "all" and status == "all":
                job = JobRequisition.objects.filter(created_by_id=manager, ticket_status=True, edited_date__range=[start, end])
            elif manager != "all" and status == "open":
                job = JobRequisition.objects.filter(created_by_id=manager, ticket_status=True, final_status=False,
                                                    edited_date__range=[start, end])
            elif manager != "all" and status == "closed":
                job = JobRequisition.objects.filter(created_by_id=manager, ticket_status=True, final_status=True,
                                                    edited_date__range=[start, end])
            else:
                pass
            data = {"job": job, "type": type, "number": number, "editaccess": edit_list}
            return render(request, "erf/job_requisition_table.html", data)
        else:
            messages.info(request, "Invalid Request. You have been logged out :)")
            return redirect("/erf/")
    elif type == "designation":
        if request.method == "POST":
            department = request.POST["department"]
            designation = request.POST.get("designation")
            start = request.POST.get("start_date")
            tomorrow = str(datetime.date.today() + datetime.timedelta(days=1))
            end = request.POST.get("end_date")
            if end:
                end = datetime.datetime.strptime(end, "%Y-%m-%d")
            else:
                end = datetime.datetime.strptime(tomorrow, "%Y-%m-%d")
            end = end + datetime.timedelta(days=1)
            if start:
                if designation:
                    job = JobRequisition.objects.filter(department=department, ticket_status=True, designation=designation,
                                                        edited_date__range=[start, end])
                else:
                    job = JobRequisition.objects.filter(department=department, ticket_status=True, edited_date__range=[start, end])
            else:
                if designation:
                    job = JobRequisition.objects.filter(department=department, ticket_status=True, designation=designation)
                else:
                    job = JobRequisition.objects.filter(department=department, ticket_status=True)

            data = {"job": job, "type": type, "number": number, "editaccess": edit_list}
            return render(request, "erf/job_requisition_table.html", data)
        else:
            messages.info(request, "Invalid Request. You have been logged out :)")
            return redirect("/erf/")

    elif type == "dead-line":
        today = datetime.date.today()
        job = JobRequisition.objects.filter(final_status=False, manager_approval=True, ticket_status=True)
        job_list = []
        for i in job:
            if i.dead_line < today:
                job_list.append(i)
        data = {"job": job_list, "type": type, "number": number, "editaccess": edit_list}
        return render(request, "erf/job_requisition_table.html", data)
    elif type == "deletion":
        job = JobRequisition.objects.filter(deletion=True, ticket_status=True)
        data = {"job": job, "type": type, "number": number, "editaccess": edit_list}
        return render(request, "erf/job_requisition_table.html", data)
    else:
        messages.info(request, "Invalid Request. You have been logged out :)")
        return redirect("/erf/")


@login_required
def jobRequisitionEditView(request, id):
    designation = request.user.profile.emp_desi
    if designation in edit_list:
        try:
            job = JobRequisition.objects.get(id=id)
            today = date.today()
            campaigns = Campaigns.objects.all()
            employees = AllAgents.objects.all()
            data = {"today": today, "job": job, "number": number, "employees": employees, "campaigns": campaigns}
            return render(request, "erf/job_requisition_edit.html", data)
        except JobRequisition.DoesNotExist:
            messages.info(request, "Invalid Request!!")
            return redirect("/erf/dashboard")
    else:
        messages.info(request, "Invalid Request. You have been logged out :)")
        return redirect("/erf/")


@login_required
def EditRequest(request):
    designation = request.user.profile.emp_desi
    emp_id = request.user.profile.emp_id
    if request.method == "POST":
        id = request.POST["id"]
        by = request.POST["by"]
        start = JobRequisition.objects.get(id=id).requisition_date.timestamp()
        timee = datetime.datetime.now(pytz.timezone('Asia/Kolkata')).timestamp() - start
        if timee <= 86400:
            if emp_id == by:
                job = JobRequisition.objects.get(id=id)
                if job.candidate_name_1:
                    messages.info(request, "Can not be edited now!")
                    return redirect("/erf/dashboard")
                else:
                    managers = Profile.objects.filter(emp_desi__in=mgr_list)
                    today = date.today()
                    campaigns = Campaigns.objects.all()
                    data = {"today": today, "managers": managers, "job": job, "campaigns": campaigns}
                    return render(request, "erf/edit_job_requisition.html", data)
            else:
                messages.info(request, "You are not authorize to edit this :)")
                return redirect("/erf/dashboard")
        else:
            messages.info(request, "Can not edit now. Time limit has been exceeded :)")
            return redirect("/erf/dashboard")
    else:
        pass


@login_required
def job_requisition_manager_edit(request):
    user = request.user.profile
    if request.method == "POST":
        weekday = datetime.datetime.now(pytz.timezone('Asia/Kolkata')).weekday()
        time = datetime.datetime.now(pytz.timezone('Asia/Kolkata')).time()
        today7pm = time.replace(hour=19, minute=0, second=0, microsecond=0)
        new_weekday = datetime.datetime.now(pytz.timezone('Asia/Kolkata')).weekday()
        edited_date = datetime.datetime.today()
        if weekday < 5:
            if time > today7pm:
                edited_date = (datetime.datetime.today() + datetime.timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0)
                new_weekday = edited_date.weekday()
        if new_weekday == 5:
            edited_date = (datetime.datetime.today() + datetime.timedelta(days=2)).replace(hour=9, minute=0, second=0, microsecond=0)
        elif new_weekday == 6:
            edited_date = (datetime.datetime.today() + datetime.timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0)
        else:
            edited_date = edited_date

        hc_req = request.POST["hc_required"]
        req_raised_by = request.POST["req_rais_by"]
        created_by_id = request.user.profile.emp_id
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
        type_of_working = request.POST["working_days"]
        working_from = request.POST.get("work_from")
        working_to = request.POST.get("work_to")
        week_no_days = request.POST.get("num_off")
        week_from = request.POST.get("off_from")
        week_to = request.POST.get("off_to")
        requisition_typ = request.POST["req_type"]
        replace_reason = request.POST["replace_reason"]
        manager_id = request.POST["manager"]
        manager = Profile.objects.get(emp_id=manager_id).emp_name
        dead_line = request.POST["dead_line"]
        campaign = request.POST["campaign"]
        id = request.POST["id"]
        pricing = request.POST["pricing"]

        csrf = request.POST["csrfmiddlewaretoken"]

        try:
            JobRequisition.objects.get(id=id, unique_id=csrf)
            messages.info(request, "Request already added. Please refresh the page!!")
            if request.user.profile.emp_desi in hr_list:
                return redirect("/erf/hr-dashboard")
            elif request.user.profile.emp_desi in am_mgr_list:
                return redirect("/erf/manager-dashboard")
            else:
                messages.info(request, "Invalid Request. You have been logged out :)")
                return redirect("/erf/")

        except JobRequisition.DoesNotExist:
            e = JobRequisition.objects.get(id=id)
            content = ""
            if e.pricing != pricing:
                content += "Edited Pricing from " + e.pricing + " to " + pricing + ", "
            if e.campaign != campaign:
                content += "Edited Campaign from " + e.campaign + " to " + campaign + ", "
            if str(e.dead_line) != dead_line:
                content += "Edited Dead Line from " + str(e.dead_line) + " to " + dead_line + ", "
            if e.type_of_working != type_of_working:
                content += "Edited Type of Working from " + e.type_of_working + " to " + type_of_working + ", "
            if str(e.hc_req) != hc_req:
                content += "Edited HC Required from " + str(e.hc_req) + " to " + hc_req + ", "
            if e.created_by_manager != manager:
                content += "Edited Manager from " + e.created_by_manager + " to " + manager + ", "
            if e.department != department:
                content += "Edited Department from " + e.department + " to " + department + ", "
            if e.designation != designation:
                content += "Edited Designation from " + e.designation + " to " + designation + ", "
            if e.process_type_one != process_typ_one:
                content += "Edited Process Type One from " + e.process_type_one + " to " + process_typ_one + ", "
            if e.process_type_two != process_typ_two:
                content += "Edited Process Type Two from " + e.process_type_two + " to " + process_typ_two + ", "
            if e.process_type_three != process_typ_three:
                content += "Edited Process Type Three from" + e.process_type_three + " to " + process_typ_three + ", "
            if str(e.salary_rang_frm) != salary_rang_frm:
                content += "Edited Salary Range From from " + str(e.salary_rang_frm) + " to " + salary_rang_frm + ", "
            if str(e.salary_rang_to) != salary_rang_to:
                content += "Edited Salary Range To from " + str(e.salary_rang_to) + " to " + salary_rang_to + ", "
            if e.qualification != qualification:
                content += "Edited Qualification from " + e.qualification + " to " + qualification + ", "
            if e.other_quali != other_quali:
                content += "Edited Other Qualification from " + e.other_quali + " to " + other_quali + ", "
            if e.skills_set != skills_set:
                content += "Edited Skill Set from " + e.skills_set + " to " + skills_set + ", "
            if str(e.languages) != str(languages):
                content += "Edited Languages from " + str(e.languages) + " to " + str(languages) + ", "
            if e.shift_timing != shift_timing:
                content += "Edited Type of Shift Timing from " + str(e.shift_timing) + " to " + str(shift_timing) + ", "
            if e.shift_timing_frm != shift_timing_frm:
                content += "Edited Shift Timing From from " + str(e.shift_timing_frm) + " to " + str(shift_timing_frm) + ", "
            if e.shift_timing_to != shift_timing_to:
                content += "Edited Shift Timing To from " + str(e.shift_timing_to) + " to " + str(shift_timing_to) + ", "
            if e.working_from != working_from:
                content += "Edited Working From from " + str(e.working_from) + " to " + str(working_from) + ", "
            if e.working_to != working_to:
                content += "Edited Working To from " + str(e.working_to) + " to " + str(working_to) + ", "
            if e.requisition_type != requisition_typ:
                content += "Edited Requisition Type from " + str(e.requisition_type) + " to " + str(requisition_typ) + ", "
            if e.reason_for_replace != replace_reason:
                content += "Edited Reason For Replace from " + str(e.reason_for_replace) + " to " + str(replace_reason) + ", "
            if week_no_days:
                if e.week_no_days != week_no_days:
                    content += "Edited Number of Week offs from " + str(e.week_no_days) + " to " + str(week_no_days) + ", "
            if week_from:
                if e.week_from != week_from:
                    content += "Edited Week off 1 from " + str(e.week_from) + " to " + str(week_from) + ", "
            if week_to:
                if e.week_to != week_to:
                    content += "Edited Week off 2 from " + str(e.week_to) + " to " + str(week_to) + ", "
            if content == "":
                content = "Nothing"

            e.pricing = pricing
            e.edited_date = edited_date
            e.unique_id = csrf
            e.campaign = campaign
            e.dead_line = dead_line
            e.type_of_working = type_of_working
            e.hc_req = hc_req
            e.req_raised_by = req_raised_by
            e.created_by_manager = manager
            e.created_by_manager_id = manager_id
            e.department = department
            e.designation = designation
            e.process_type_one = process_typ_one
            e.process_type_two = process_typ_two
            e.process_type_three = process_typ_three
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
            if week_no_days:
                e.week_no_days = week_no_days
            if week_from:
                e.week_from = week_from
            if week_to:
                e.week_to = week_to
            e.requisition_type = requisition_typ
            e.reason_for_replace = replace_reason
            e.created_by_id = created_by_id
            e.save()
            a = Tickets.objects.get(job_requisition_id=id)
            now_datetime = datetime.datetime.now().strftime('%b %d,%Y %H:%M:%S')
            edited_by = str(
                [now_datetime, request.user.profile.emp_name, request.user.profile.emp_id, "( "+content+" )"])
            previous = a.edited_by
            adding = previous + ",\n" + edited_by
            a.edited_by = adding
            a.save()
            messages.info(request, "Requisition Updated Successfully !!")

            action = "Edited"
            subject = action + " - Employee Requisition [" + str(e.id) +"]"
            html_path = 'erf/email.html'
            data = {'id': e.id, "created_date": e.edited_date, "hc": e.hc_req, "department": e.department,
                    "position": e.designation,
                    "deadline": e.dead_line, "campaign": e.campaign, "user": request.user.profile.emp_name,
                    "action": action, "status": e.request_status,"content":content}
            email_template = get_template(html_path).render(data)
            manager_email = Profile.objects.get(emp_id=manager_id).emp_email
            try:
                rm1_email = Profile.objects.get(emp_id=e.created_by_rm1_id).emp_email
            except Profile.DoesNotExist:
                rm1_email = request.user.profile.emp_email
            to = [request.user.profile.emp_email, "ta@expertcallers.com","dina@expertcallers.com","joseph@expertcallers.com", manager_email, rm1_email]
            email_msg = EmailMessage(subject,
                                     email_template, 'erf@expertcallers.com',
                                     to,
                                     reply_to=['erf@expertcallers.com'])
            email_msg.content_subtype = 'html'
            email_msg.send(fail_silently=False)
            designation = request.user.profile.emp_desi
            if designation in hr_list:
                return redirect("/erf/hr-dashboard")
            elif designation in am_mgr_list:
                return redirect("/erf/manager-dashboard")
    else:
        messages.info(request, "Invalid Request. You have been logged out :)")
        return redirect("/erf/")


@login_required
def jobRequisitionEditUpdate(request):
    if request.method == "POST":
        id = request.POST["id"]
        candidate_remark = request.POST["can_remark"]
        comments = request.POST["comments"]
        closure_date = request.POST.get("clos_date")
        candidate_name_1 = request.POST.get("cand_name_1")
        source_1 = request.POST.get("source_1")
        referral_emp_name_1 = request.POST.get("emp_name_1")
        referral_emp_id_1 = request.POST.get("emp_id_1")
        social_1 = request.POST.get("social_1")
        partner_1 = request.POST.get("partner_1")
        candidate_name_2 = request.POST.get("cand_name_2")
        source_2 = request.POST.get("source_2")
        referral_emp_name_2 = request.POST.get("emp_name_2")
        referral_emp_id_2 = request.POST.get("emp_id_2")
        social_2 = request.POST.get("social_2")
        partner_2 = request.POST.get("partner_2")
        candidate_name_3 = request.POST.get("cand_name_3")
        source_3 = request.POST.get("source_3")
        referral_emp_name_3 = request.POST.get("emp_name_3")
        referral_emp_id_3 = request.POST.get("emp_id_3")
        social_3 = request.POST.get("social_3")
        partner_3 = request.POST.get("partner_3")
        candidate_name_4 = request.POST.get("cand_name_4")
        source_4 = request.POST.get("source_4")
        referral_emp_name_4 = request.POST.get("emp_name_4")
        referral_emp_id_4 = request.POST.get("emp_id_4")
        social_4 = request.POST.get("social_4")
        partner_4 = request.POST.get("partner_4")
        candidate_name_5 = request.POST.get("cand_name_5")
        source_5 = request.POST.get("source_5")
        referral_emp_name_5 = request.POST.get("emp_name_5")
        referral_emp_id_5 = request.POST.get("emp_id_5")
        social_5 = request.POST.get("social_5")
        partner_5 = request.POST.get("partner_5")
        candidate_name_6 = request.POST.get("cand_name_6")
        source_6 = request.POST.get("source_6")
        referral_emp_name_6 = request.POST.get("emp_name_6")
        referral_emp_id_6 = request.POST.get("emp_id_6")
        social_6 = request.POST.get("social_6")
        partner_6 = request.POST.get("partner_6")
        candidate_name_7 = request.POST.get("cand_name_7")
        source_7 = request.POST.get("source_7")
        referral_emp_name_7 = request.POST.get("emp_name_7")
        referral_emp_id_7 = request.POST.get("emp_id_7")
        social_7 = request.POST.get("social_7")
        partner_7 = request.POST.get("partner_7")
        candidate_name_8 = request.POST.get("cand_name_8")
        source_8 = request.POST.get("source_8")
        referral_emp_name_8 = request.POST.get("emp_name_8")
        referral_emp_id_8 = request.POST.get("emp_id_8")
        social_8 = request.POST.get("social_8")
        partner_8 = request.POST.get("partner_8")
        candidate_name_9 = request.POST.get("cand_name_9")
        source_9 = request.POST.get("source_9")
        referral_emp_name_9 = request.POST.get("emp_name_9")
        referral_emp_id_9 = request.POST.get("emp_id_9")
        social_9 = request.POST.get("social_9")
        partner_9 = request.POST.get("partner_9")
        candidate_name_10 = request.POST.get("cand_name_10")
        source_10 = request.POST.get("source_10")
        referral_emp_name_10 = request.POST.get("emp_name_10")
        referral_emp_id_10 = request.POST.get("emp_id_10")
        social_10 = request.POST.get("social_10")
        partner_10 = request.POST.get("partner_10")
        candidate_name_11 = request.POST.get("cand_name_11")
        source_11 = request.POST.get("source_11")
        referral_emp_name_11 = request.POST.get("emp_name_11")
        referral_emp_id_11 = request.POST.get("emp_id_11")
        social_11 = request.POST.get("social_11")
        partner_11 = request.POST.get("partner_11")
        candidate_name_12 = request.POST.get("cand_name_12")
        source_12 = request.POST.get("source_12")
        referral_emp_name_12 = request.POST.get("emp_name_12")
        referral_emp_id_12 = request.POST.get("emp_id_12")
        social_12 = request.POST.get("social_12")
        partner_12 = request.POST.get("partner_12")
        candidate_name_13 = request.POST.get("cand_name_13")
        source_13 = request.POST.get("source_13")
        referral_emp_name_13 = request.POST.get("emp_name_13")
        referral_emp_id_13 = request.POST.get("emp_id_13")
        social_13 = request.POST.get("social_13")
        partner_13 = request.POST.get("partner_13")
        candidate_name_14 = request.POST.get("cand_name_14")
        source_14 = request.POST.get("source_14")
        referral_emp_name_14 = request.POST.get("emp_name_14")
        referral_emp_id_14 = request.POST.get("emp_id_14")
        social_14 = request.POST.get("social_14")
        partner_14 = request.POST.get("partner_14")
        candidate_name_15 = request.POST.get("cand_name_15")
        source_15 = request.POST.get("source_15")
        referral_emp_name_15 = request.POST.get("emp_name_15")
        referral_emp_id_15 = request.POST.get("emp_id_15")
        social_15 = request.POST.get("social_15")
        partner_15 = request.POST.get("partner_15")
        candidate_name_16 = request.POST.get("cand_name_16")
        source_16 = request.POST.get("source_16")
        referral_emp_name_16 = request.POST.get("emp_name_16")
        referral_emp_id_16 = request.POST.get("emp_id_16")
        social_16 = request.POST.get("social_16")
        partner_16 = request.POST.get("partner_16")
        candidate_name_17 = request.POST.get("cand_name_17")
        source_17 = request.POST.get("source_17")
        referral_emp_name_17 = request.POST.get("emp_name_17")
        referral_emp_id_17 = request.POST.get("emp_id_17")
        social_17 = request.POST.get("social_17")
        partner_17 = request.POST.get("partner_17")
        candidate_name_18 = request.POST.get("cand_name_18")
        source_18 = request.POST.get("source_18")
        referral_emp_name_18 = request.POST.get("emp_name_18")
        referral_emp_id_18 = request.POST.get("emp_id_18")
        social_18 = request.POST.get("social_18")
        partner_18 = request.POST.get("partner_18")
        candidate_name_19 = request.POST.get("cand_name_19")
        source_19 = request.POST.get("source_19")
        referral_emp_name_19 = request.POST.get("emp_name_19")
        referral_emp_id_19 = request.POST.get("emp_id_19")
        social_19 = request.POST.get("social_19")
        partner_19 = request.POST.get("partner_19")
        candidate_name_20 = request.POST.get("cand_name_20")
        source_20 = request.POST.get("source_20")
        referral_emp_name_20 = request.POST.get("emp_name_20")
        referral_emp_id_20 = request.POST.get("emp_id_20")
        social_20 = request.POST.get("social_20")
        partner_20 = request.POST.get("partner_20")

        source_internal_emp_id_1 = request.POST.get("internal_emp_id_1")
        source_internal_campaign_name_1 = request.POST.get("internal_campaign_1")
        source_internal_emp_id_2 = request.POST.get("internal_emp_id_2")
        source_internal_campaign_name_2 = request.POST.get("internal_campaign_2")
        source_internal_emp_id_3 = request.POST.get("internal_emp_id_3")
        source_internal_campaign_name_3 = request.POST.get("internal_campaign_3")
        source_internal_emp_id_4 = request.POST.get("internal_emp_id_4")
        source_internal_campaign_name_4 = request.POST.get("internal_campaign_4")
        source_internal_emp_id_5 = request.POST.get("internal_emp_id_5")
        source_internal_campaign_name_5 = request.POST.get("internal_campaign_5")
        source_internal_emp_id_6 = request.POST.get("internal_emp_id_6")
        source_internal_campaign_name_6 = request.POST.get("internal_campaign_6")
        source_internal_emp_id_7 = request.POST.get("internal_emp_id_7")
        source_internal_campaign_name_7 = request.POST.get("internal_campaign_7")
        source_internal_emp_id_8 = request.POST.get("internal_emp_id_8")
        source_internal_campaign_name_8 = request.POST.get("internal_campaign_8")
        source_internal_emp_id_9 = request.POST.get("internal_emp_id_9")
        source_internal_campaign_name_9 = request.POST.get("internal_campaign_9")
        source_internal_emp_id_10 = request.POST.get("internal_emp_id_10")
        source_internal_campaign_name_10 = request.POST.get("internal_campaign_10")
        source_internal_emp_id_11 = request.POST.get("internal_emp_id_11")
        source_internal_campaign_name_11 = request.POST.get("internal_campaign_11")
        source_internal_emp_id_12 = request.POST.get("internal_emp_id_12")
        source_internal_campaign_name_12 = request.POST.get("internal_campaign_12")
        source_internal_emp_id_13 = request.POST.get("internal_emp_id_13")
        source_internal_campaign_name_13 = request.POST.get("internal_campaign_13")
        source_internal_emp_id_14 = request.POST.get("internal_emp_id_14")
        source_internal_campaign_name_14 = request.POST.get("internal_campaign_14")
        source_internal_emp_id_15 = request.POST.get("internal_emp_id_15")
        source_internal_campaign_name_15 = request.POST.get("internal_campaign_15")
        source_internal_emp_id_16 = request.POST.get("internal_emp_id_16")
        source_internal_campaign_name_16 = request.POST.get("internal_campaign_16")
        source_internal_emp_id_17 = request.POST.get("internal_emp_id_17")
        source_internal_campaign_name_17 = request.POST.get("internal_campaign_17")
        source_internal_emp_id_18 = request.POST.get("internal_emp_id_18")
        source_internal_campaign_name_18 = request.POST.get("internal_campaign_18")
        source_internal_emp_id_19 = request.POST.get("internal_emp_id_19")
        source_internal_campaign_name_19 = request.POST.get("internal_campaign_19")
        source_internal_emp_id_20 = request.POST.get("internal_emp_id_20")
        source_internal_campaign_name_20 = request.POST.get("internal_campaign_20")
        if source_internal_emp_id_1:
            source_internal_emp_name_1 = AllAgents.objects.get(emp_id=source_internal_emp_id_1).emp_name
        if source_internal_emp_id_2:
            source_internal_emp_name_2 = AllAgents.objects.get(emp_id=source_internal_emp_id_2).emp_name
        if source_internal_emp_id_3:
            source_internal_emp_name_3 = AllAgents.objects.get(emp_id=source_internal_emp_id_3).emp_name
        if source_internal_emp_id_4:
            source_internal_emp_name_4 = AllAgents.objects.get(emp_id=source_internal_emp_id_4).emp_name
        if source_internal_emp_id_5:
            source_internal_emp_name_5 = AllAgents.objects.get(emp_id=source_internal_emp_id_5).emp_name
        if source_internal_emp_id_6:
            source_internal_emp_name_6 = AllAgents.objects.get(emp_id=source_internal_emp_id_6).emp_name
        if source_internal_emp_id_7:
            source_internal_emp_name_7 = AllAgents.objects.get(emp_id=source_internal_emp_id_7).emp_name
        if source_internal_emp_id_8:
            source_internal_emp_name_8 = AllAgents.objects.get(emp_id=source_internal_emp_id_8).emp_name
        if source_internal_emp_id_9:
            source_internal_emp_name_9 = AllAgents.objects.get(emp_id=source_internal_emp_id_9).emp_name
        if source_internal_emp_id_10:
            source_internal_emp_name_10 = AllAgents.objects.get(emp_id=source_internal_emp_id_10).emp_name
        if source_internal_emp_id_11:
            source_internal_emp_name_11 = AllAgents.objects.get(emp_id=source_internal_emp_id_11).emp_name
        if source_internal_emp_id_12:
            source_internal_emp_name_12 = AllAgents.objects.get(emp_id=source_internal_emp_id_12).emp_name
        if source_internal_emp_id_13:
            source_internal_emp_name_13 = AllAgents.objects.get(emp_id=source_internal_emp_id_13).emp_name
        if source_internal_emp_id_14:
            source_internal_emp_name_14 = AllAgents.objects.get(emp_id=source_internal_emp_id_14).emp_name
        if source_internal_emp_id_15:
            source_internal_emp_name_15 = AllAgents.objects.get(emp_id=source_internal_emp_id_15).emp_name
        if source_internal_emp_id_16:
            source_internal_emp_name_16 = AllAgents.objects.get(emp_id=source_internal_emp_id_16).emp_name
        if source_internal_emp_id_17:
            source_internal_emp_name_17 = AllAgents.objects.get(emp_id=source_internal_emp_id_17).emp_name
        if source_internal_emp_id_18:
            source_internal_emp_name_18 = AllAgents.objects.get(emp_id=source_internal_emp_id_18).emp_name
        if source_internal_emp_id_19:
            source_internal_emp_name_19 = AllAgents.objects.get(emp_id=source_internal_emp_id_19).emp_name
        if source_internal_emp_id_20:
            source_internal_emp_name_20 = AllAgents.objects.get(emp_id=source_internal_emp_id_20).emp_name


        interviewer1 = request.POST.get("inter_name_1")
        interviewer_2 = request.POST.get("inter_name_2")
        interviewer_3 = request.POST.get("inter_name_3")
        interviewer_4 = request.POST.get("inter_name_4")
        interviewer_5 = request.POST.get("inter_name_5")
        interviewer_6 = request.POST.get("inter_name_6")
        interviewer_7 = request.POST.get("inter_name_7")
        interviewer_8 = request.POST.get("inter_name_8")
        interviewer_9 = request.POST.get("inter_name_9")
        interviewer_10 = request.POST.get("inter_name_10")
        interviewer_11 = request.POST.get("inter_name_11")
        interviewer_12 = request.POST.get("inter_name_12")
        interviewer_13 = request.POST.get("inter_name_13")
        interviewer_14 = request.POST.get("inter_name_14")
        interviewer_15 = request.POST.get("inter_name_15")
        interviewer_16 = request.POST.get("inter_name_16")
        interviewer_17 = request.POST.get("inter_name_17")
        interviewer_18 = request.POST.get("inter_name_18")
        interviewer_19 = request.POST.get("inter_name_19")
        interviewer_20 = request.POST.get("inter_name_20")
        interviewer_id_1 = request.POST.get('inter_id_1')
        interviewer_id_2 = request.POST.get('inter_id_2')
        interviewer_id_3 = request.POST.get('inter_id_3')
        interviewer_id_4 = request.POST.get('inter_id_4')
        interviewer_id_5 = request.POST.get('inter_id_5')
        interviewer_id_6 = request.POST.get('inter_id_6')
        interviewer_id_7 = request.POST.get('inter_id_7')
        interviewer_id_8 = request.POST.get('inter_id_8')
        interviewer_id_9 = request.POST.get('inter_id_9')
        interviewer_id_10 = request.POST.get('inter_id_10')
        interviewer_id_11 = request.POST.get('inter_id_11')
        interviewer_id_12 = request.POST.get('inter_id_12')
        interviewer_id_13 = request.POST.get('inter_id_13')
        interviewer_id_14 = request.POST.get('inter_id_14')
        interviewer_id_15 = request.POST.get('inter_id_15')
        interviewer_id_16 = request.POST.get('inter_id_16')
        interviewer_id_17 = request.POST.get('inter_id_17')
        interviewer_id_18 = request.POST.get('inter_id_18')
        interviewer_id_19 = request.POST.get('inter_id_19')
        interviewer_id_20 = request.POST.get('inter_id_20')

        today = str(datetime.date.today())
        recruited_people = request.POST["rec_peo"]
        request_status = request.POST.get("req_status")
        csrf = request.POST["csrfmiddlewaretoken"]
        if request_status == "Completed":
            request_status = "Waiting For Manager Approval"
            unique = csrf
        else:
            request_status = "Pending"
            unique = csrf

        try:
            JobRequisition.objects.get(id=id, unique_id=unique)
            messages.info(request, "Requisition Updated Successfully !!")
            if request.user.profile.emp_desi in hr_list:
                return redirect("/erf/hr-dashboard")
            elif request.user.profile.emp_desi in am_mgr_list:
                return redirect("/erf/manager-dashboard")
            else:
                messages.info(request, "Invalid Request. You have been logged out :)")
                return redirect("/erf/")
        except JobRequisition.DoesNotExist:
            e = JobRequisition.objects.get(id=id)
            e.interviewer1 = interviewer1
            e.interviewer_2 = interviewer_2
            e.interviewer_3 = interviewer_3
            e.interviewer_4 = interviewer_4
            e.interviewer_5 = interviewer_5
            e.interviewer_6 = interviewer_6
            e.interviewer_7 = interviewer_7
            e.interviewer_8 = interviewer_8
            e.interviewer_9 = interviewer_9
            e.interviewer_10 = interviewer_10
            e.interviewer_11 = interviewer_11
            e.interviewer_12 = interviewer_12
            e.interviewer_13 = interviewer_13
            e.interviewer_14 = interviewer_14
            e.interviewer_15 = interviewer_15
            e.interviewer_16 = interviewer_16
            e.interviewer_17 = interviewer_17
            e.interviewer_18 = interviewer_18
            e.interviewer_19 = interviewer_19
            e.interviewer_20 = interviewer_20
            e.interviewer_id_1 = interviewer_id_1
            e.interviewer_id_2 = interviewer_id_2
            e.interviewer_id_3 = interviewer_id_3
            e.interviewer_id_4 = interviewer_id_4
            e.interviewer_id_5 = interviewer_id_5
            e.interviewer_id_6 = interviewer_id_6
            e.interviewer_id_7 = interviewer_id_7
            e.interviewer_id_8 = interviewer_id_8
            e.interviewer_id_9 = interviewer_id_9
            e.interviewer_id_10 = interviewer_id_10
            e.interviewer_id_11 = interviewer_id_11
            e.interviewer_id_12 = interviewer_id_12
            e.interviewer_id_13 = interviewer_id_13
            e.interviewer_id_14 = interviewer_id_14
            e.interviewer_id_15 = interviewer_id_15
            e.interviewer_id_16 = interviewer_id_16
            e.interviewer_id_17 = interviewer_id_17
            e.interviewer_id_18 = interviewer_id_18
            e.interviewer_id_19 = interviewer_id_19
            e.interviewer_id_20 = interviewer_id_20
            e.unique_id = unique
            if request_status == "Waiting For Manager Approval":
                e.initial_status = True
                e.closed_by = request.user.profile.emp_name
                e.closed_by_id = request.user.profile.emp_id

            if closure_date:
                e.closure_date = closure_date

            if candidate_name_1:
                e.candidate_name_1 = candidate_name_1
                e.source_1 = source_1
                e.source_emp_name_1 = referral_emp_name_1
                e.source_emp_id_1 = referral_emp_id_1
                if source_internal_emp_id_1:
                    e.source_internal_emp_name_1 = source_internal_emp_name_1
                e.source_internal_emp_id_1 = source_internal_emp_id_1
                e.source_internal_campaign_name_1 = source_internal_campaign_name_1
                e.source_social_1 = social_1
                e.source_partners_1 = partner_1
            if candidate_name_2:
                e.candidate_name_2 = candidate_name_2
                e.source_2 = source_2
                e.source_emp_name_2 = referral_emp_name_2
                e.source_emp_id_2 = referral_emp_id_2
                if source_internal_emp_id_2:
                    e.source_internal_emp_name_2 = source_internal_emp_name_2
                e.source_internal_emp_id_2 = source_internal_emp_id_2
                e.source_internal_campaign_name_2 = source_internal_campaign_name_2
                e.source_social_2 = social_2
                e.source_partners_2 = partner_2
            if candidate_name_3:
                e.candidate_name_3 = candidate_name_3
                e.source_3 = source_3
                e.source_emp_name_3 = referral_emp_name_3
                e.source_emp_id_3 = referral_emp_id_3
                if source_internal_emp_id_3:
                    e.source_internal_emp_name_3 = source_internal_emp_name_3
                e.source_internal_emp_id_3 = source_internal_emp_id_3
                e.source_internal_campaign_name_3 = source_internal_campaign_name_3
                e.source_social_3 = social_3
                e.source_partners_3 = partner_3
            if candidate_name_4:
                e.candidate_name_4 = candidate_name_4
                e.source_4 = source_4
                e.source_emp_name_4 = referral_emp_name_4
                e.source_emp_id_4 = referral_emp_id_4
                if source_internal_emp_id_4:
                    e.source_internal_emp_name_4 = source_internal_emp_name_4
                e.source_internal_emp_id_4 = source_internal_emp_id_4
                e.source_internal_campaign_name_4 = source_internal_campaign_name_4
                e.source_social_4 = social_4
                e.source_partners_4 = partner_4
            if candidate_name_5:
                e.candidate_name_5 = candidate_name_5
                e.source_5 = source_5
                e.source_emp_name_5 = referral_emp_name_5
                e.source_emp_id_5 = referral_emp_id_5
                if source_internal_emp_id_5:
                    e.source_internal_emp_name_5 = source_internal_emp_name_5
                e.source_internal_emp_id_5 = source_internal_emp_id_5
                e.source_internal_campaign_name_5 = source_internal_campaign_name_5
                e.source_social_5 = social_5
                e.source_partners_5 = partner_5
            if candidate_name_6:
                e.candidate_name_6 = candidate_name_6
                e.source_6 = source_6
                e.source_emp_name_6 = referral_emp_name_6
                e.source_emp_id_6 = referral_emp_id_6
                if source_internal_emp_id_6:
                    e.source_internal_emp_name_6 = source_internal_emp_name_6
                e.source_internal_emp_id_6 = source_internal_emp_id_6
                e.source_internal_campaign_name_6 = source_internal_campaign_name_6
                e.source_social_6 = social_6
                e.source_partners_6 = partner_6
            if candidate_name_7:
                e.candidate_name_7 = candidate_name_7
                e.source_7 = source_7
                e.source_emp_name_7 = referral_emp_name_7
                e.source_emp_id_7 = referral_emp_id_7
                if source_internal_emp_id_7:
                    e.source_internal_emp_name_7 = source_internal_emp_name_7
                e.source_internal_emp_id_7 = source_internal_emp_id_7
                e.source_internal_campaign_name_7 = source_internal_campaign_name_7
                e.source_social_7 = social_7
                e.source_partners_7 = partner_7
            if candidate_name_8:
                e.candidate_name_8 = candidate_name_8
                e.source_8 = source_8
                e.source_emp_name_8 = referral_emp_name_8
                e.source_emp_id_8 = referral_emp_id_8
                if source_internal_emp_id_8:
                    e.source_internal_emp_name_8 = source_internal_emp_name_8
                e.source_internal_emp_id_8 = source_internal_emp_id_8
                e.source_internal_campaign_name_8 = source_internal_campaign_name_8
                e.source_social_8 = social_8
                e.source_partners_8 = partner_8
            if candidate_name_9:
                e.candidate_name_9 = candidate_name_9
                e.source_9 = source_9
                e.source_emp_name_9 = referral_emp_name_9
                e.source_emp_id_9 = referral_emp_id_9
                if source_internal_emp_id_9:
                    e.source_internal_emp_name_9 = source_internal_emp_name_9
                e.source_internal_emp_id_9 = source_internal_emp_id_9
                e.source_internal_campaign_name_9 = source_internal_campaign_name_9
                e.source_social_9 = social_9
                e.source_partners_9 = partner_9
            if candidate_name_10:
                e.candidate_name_10 = candidate_name_10
                e.source_10 = source_10
                e.source_emp_name_10 = referral_emp_name_10
                e.source_emp_id_10 = referral_emp_id_10
                if source_internal_emp_id_10:
                    e.source_internal_emp_name_10 = source_internal_emp_name_10
                e.source_internal_emp_id_10 = source_internal_emp_id_10
                e.source_internal_campaign_name_10 = source_internal_campaign_name_10
                e.source_social_10 = social_10
                e.source_partners_10 = partner_10
            if candidate_name_11:
                e.candidate_name_11 = candidate_name_11
                e.source_11 = source_11
                e.source_emp_name_11 = referral_emp_name_11
                e.source_emp_id_11 = referral_emp_id_11
                if source_internal_emp_id_11:
                    e.source_internal_emp_name_11 = source_internal_emp_name_11
                e.source_internal_emp_id_11 = source_internal_emp_id_11
                e.source_internal_campaign_name_11 = source_internal_campaign_name_11
                e.source_social_11 = social_11
                e.source_partners_11 = partner_11
            if candidate_name_12:
                e.candidate_name_12 = candidate_name_12
                e.source_12 = source_12
                e.source_emp_name_12 = referral_emp_name_12
                e.source_emp_id_12 = referral_emp_id_12
                if source_internal_emp_id_12:
                    e.source_internal_emp_name_12 = source_internal_emp_name_12
                e.source_internal_emp_id_12 = source_internal_emp_id_12
                e.source_internal_campaign_name_12 = source_internal_campaign_name_12
                e.source_social_12 = social_12
                e.source_partners_12 = partner_12
            if candidate_name_13:
                e.candidate_name_13 = candidate_name_13
                e.source_13 = source_13
                e.source_emp_name_13 = referral_emp_name_13
                e.source_emp_id_13 = referral_emp_id_13
                if source_internal_emp_id_13:
                    e.source_internal_emp_name_13 = source_internal_emp_name_13
                e.source_internal_emp_id_13 = source_internal_emp_id_13
                e.source_internal_campaign_name_13 = source_internal_campaign_name_13
                e.source_social_13 = social_13
                e.source_partners_13 = partner_13
            if candidate_name_14:
                e.candidate_name_14 = candidate_name_14
                e.source_14 = source_14
                e.source_emp_name_14 = referral_emp_name_14
                e.source_emp_id_14 = referral_emp_id_14
                if source_internal_emp_id_14:
                    e.source_internal_emp_name_14 = source_internal_emp_name_14
                e.source_internal_emp_id_14 = source_internal_emp_id_14
                e.source_internal_campaign_name_14 = source_internal_campaign_name_14
                e.source_social_14 = social_14
                e.source_partners_14 = partner_14
            if candidate_name_15:
                e.candidate_name_15 = candidate_name_15
                e.source_15 = source_15
                e.source_emp_name_15 = referral_emp_name_15
                e.source_emp_id_15 = referral_emp_id_15
                if source_internal_emp_id_15:
                    e.source_internal_emp_name_15 = source_internal_emp_name_15
                e.source_internal_emp_id_15 = source_internal_emp_id_15
                e.source_internal_campaign_name_15 = source_internal_campaign_name_15
                e.source_social_15 = social_15
                e.source_partners_15 = partner_15
            if candidate_name_16:
                e.candidate_name_16 = candidate_name_16
                e.source_16 = source_16
                e.source_emp_name_16 = referral_emp_name_16
                e.source_emp_id_16 = referral_emp_id_16
                if source_internal_emp_id_16:
                    e.source_internal_emp_name_16 = source_internal_emp_name_16
                e.source_internal_emp_id_16 = source_internal_emp_id_16
                e.source_internal_campaign_name_16 = source_internal_campaign_name_16
                e.source_social_16 = social_16
                e.source_partners_16 = partner_16
            if candidate_name_17:
                e.candidate_name_17 = candidate_name_17
                e.source_17 = source_17
                e.source_emp_name_17 = referral_emp_name_17
                e.source_emp_id_17 = referral_emp_id_17
                if source_internal_emp_id_17:
                    e.source_internal_emp_name_17 = source_internal_emp_name_17
                e.source_internal_emp_id_17 = source_internal_emp_id_17
                e.source_internal_campaign_name_17 = source_internal_campaign_name_17
                e.source_social_17 = social_17
                e.source_partners_17 = partner_17
            if candidate_name_18:
                e.candidate_name_18 = candidate_name_18
                e.source_18 = source_18
                e.source_emp_name_18 = referral_emp_name_18
                e.source_emp_id_18 = referral_emp_id_18
                if source_internal_emp_id_18:
                    e.source_internal_emp_name_18 = source_internal_emp_name_18
                e.source_internal_emp_id_18 = source_internal_emp_id_18
                e.source_internal_campaign_name_18 = source_internal_campaign_name_18
                e.source_social_18 = social_18
                e.source_partners_18 = partner_18
            if candidate_name_19:
                e.candidate_name_19 = candidate_name_19
                e.source_19 = source_19
                e.source_emp_name_19 = referral_emp_name_19
                e.source_emp_id_19 = referral_emp_id_19
                if source_internal_emp_id_19:
                    e.source_internal_emp_name_19 = source_internal_emp_name_19
                e.source_internal_emp_id_19 = source_internal_emp_id_19
                e.source_internal_campaign_name_19 = source_internal_campaign_name_19
                e.source_social_19 = social_19
                e.source_partners_19 = partner_19
            if candidate_name_20:
                e.candidate_name_20 = candidate_name_20
                e.source_20 = source_20
                e.source_emp_name_20 = referral_emp_name_20
                e.source_emp_id_20 = referral_emp_id_20
                if source_internal_emp_id_20:
                    e.source_internal_emp_name_20 = source_internal_emp_name_20
                e.source_internal_emp_id_20 = source_internal_emp_id_20
                e.source_internal_campaign_name_20 = source_internal_campaign_name_20
                e.source_social_20 = social_20
                e.source_partners_20 = partner_20

            e.recruited_people = recruited_people
            e.request_status = request_status
            e.candidate_remark = candidate_remark
            e.save()
            a = Tickets.objects.get(job_requisition_id=id)
            now_datetime = datetime.datetime.now().strftime('%b %d,%Y %H:%M:%S')
            edited_name = request.user.profile.emp_name
            edited_id = request.user.profile.emp_id
            edited_by = str([now_datetime, edited_name, edited_id, comments])
            previous = a.edited_by
            adding = previous + ",\n" + edited_by
            a.edited_by = adding
            a.save()
            messages.info(request, "Requisition Updated Successfully !!")

            action = "Updated"
            subject = action + " - Employee Requisition [" + str(e.id) +"]"
            html_path = 'erf/email.html'
            data = {'id': e.id, "created_date": e.edited_date, "hc": e.hc_req, "department": e.department,
                    "position": e.designation,
                    "deadline": e.dead_line, "campaign": e.campaign, "user": request.user.profile.emp_name,
                    "action": action, "status": e.request_status}
            email_template = get_template(html_path).render(data)
            creater_id = e.created_by_id
            creater_email = Profile.objects.get(emp_id=creater_id).emp_email
            manager_id = e.created_by_manager_id
            manager_email = Profile.objects.get(emp_id=manager_id).emp_email
            try:
                rm1_email = Profile.objects.get(emp_id=e.created_by_rm1_id).emp_email
            except Profile.DoesNotExist:
                rm1_email = creater_email
            to = [request.user.profile.emp_email, "ta@expertcallers.com","dina@expertcallers.com","joseph@expertcallers.com", creater_email, manager_email, rm1_email]
            email_msg = EmailMessage(subject,
                                     email_template, 'erf@expertcallers.com',
                                     to,
                                     reply_to=['erf@expertcallers.com'])
            email_msg.content_subtype = 'html'
            email_msg.send(fail_silently=False)

            if request.user.profile.emp_desi in hr_list:
                return redirect("/erf/hr-dashboard")
            elif request.user.profile.emp_desi in am_mgr_list:
                return redirect("/erf/manager-dashboard")
            else:
                messages.info(request, "Invalid Request. You have been logged out :)")
                return redirect("/erf/")
    else:
        messages.info(request, "Invalid Request. You have been logged out :)")
        return redirect("/erf/")


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated! Please login with new password.')
            user = request.user
            user.profile.pc = True
            user.save()
            user.profile.save()
            return redirect('/erf/')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'erf/settings.html', {'form': form})

@login_required
def approval(request):
    if request.method == "POST":
        id = request.POST["id"]
        response = request.POST["response"]
        if response == "Approve":
            request_status = "Approved and Complete"
        if response == "Reject":
            request_status = "Rejected by Manager"
        try:
            JobRequisition.objects.get(id=id, request_status=request_status)
            messages.info(request, "Changes have been done please refresh the page!")
            if request.user.profile.emp_desi in hr_list:
                return redirect("/erf/hr-dashboard")
            elif request.user.profile.emp_desi in am_mgr_list:
                return redirect("/erf/manager-dashboard")
            else:
                messages.info(request, "Invalid Request. You have been logged out :)")
                return redirect("/erf/")
        except JobRequisition.DoesNotExist:
            e = JobRequisition.objects.get(id=id)
            a = Tickets.objects.get(job_requisition_id=id)
            if response == "Approve":
                e.final_status = True
                e.request_status = request_status
                comment = "Approved and Complete"
                action = "Approved"
                message = "Approved Successfully!!"
            if response == "Reject":
                e.initial_status = False
                e.request_status = request_status
                comment = "Rejected by Manager"
                action = "Rejected"
                message = "Requisition Rejected."
            e.save()
            now_datetime = datetime.datetime.now().strftime('%b %d,%Y %H:%M:%S')
            edited_name = request.user.profile.emp_name
            edited_id = request.user.profile.emp_id
            edited_by = str([now_datetime, edited_name, edited_id, comment])
            previous = a.edited_by
            adding = previous + ",\n" + edited_by
            a.edited_by = adding
            a.save()
            messages.info(request, message)

            subject = action + " - Employee Requisition [" + str(e.id) + "]"
            html_path = 'erf/email.html'
            data = {'id': e.id, "created_date": e.edited_date, "hc": e.hc_req, "department": e.department,
                    "position": e.designation,
                    "deadline": e.dead_line, "campaign": e.campaign, "user": request.user.profile.emp_name,
                    "action": action, "status": e.request_status}
            email_template = get_template(html_path).render(data)
            creater_id = e.created_by_id
            creater_email = Profile.objects.get(emp_id=creater_id).emp_email
            try:
                rm1_email = Profile.objects.get(emp_id=e.created_by_rm1_id).emp_email
            except Profile.DoesNotExist:
                rm1_email = creater_email
            to = [request.user.profile.emp_email, "ta@expertcallers.com","dina@expertcallers.com","joseph@expertcallers.com", creater_email, rm1_email]
            email_msg = EmailMessage(subject,
                                     email_template, 'erf@expertcallers.com',
                                     to,
                                     reply_to=['erf@expertcallers.com'])
            email_msg.content_subtype = 'html'
            email_msg.send(fail_silently=False)
            if request.user.profile.emp_desi in hr_list:
                return redirect("/erf/hr-dashboard")
            elif request.user.profile.emp_desi in am_mgr_list:
                return redirect("/erf/manager-dashboard")
            else:
                messages.info(request, "Invalid Request. You have been logged out :)")
                return redirect("/erf/")
    else:
        messages.info(request, "Invalid Request. You have been logged out :)")
        return redirect("/erf/")

@login_required
def ExportReport(request, type):
    if type == "status":
        if request.method == "POST":
            manager = request.POST["manager"]
            status = request.POST["status"]
            start = request.POST["start_date"]
            tomorrow = str(datetime.date.today() + datetime.timedelta(days=1))
            end = request.POST.get("end_date")
            if end:
                end = datetime.datetime.strptime(end, "%Y-%m-%d")
            else:
                end = datetime.datetime.strptime(tomorrow, "%Y-%m-%d")
            end = end + datetime.timedelta(days=1)
            if manager == "all" and status == "all":
                job = JobRequisition.objects.filter(edited_date__range=[start, end])
            elif manager == "all" and status == "open":
                job = JobRequisition.objects.filter(final_status=False, edited_date__range=[start, end])
            elif manager == "all" and status == "closed":
                job = JobRequisition.objects.filter(final_status=True, edited_date__range=[start, end])
            elif manager != "all" and status == "all":
                job = JobRequisition.objects.filter(created_by_id=manager, edited_date__range=[start, end])
            elif manager != "all" and status == "open":
                job = JobRequisition.objects.filter(created_by_id=manager, final_status=False,
                                                    edited_date__range=[start, end])
            elif manager != "all" and status == "closed":
                job = JobRequisition.objects.filter(created_by_id=manager, final_status=True,
                                                    edited_date__range=[start, end])
            else:
                pass
            data = {"job": job, "type": type, "number": number, "editaccess": edit_list}
            return render(request, "erf/export_table.html", data)
        else:
            messages.info(request, "Invalid Request. You have been logged out :)")
            return redirect("/erf/")
    elif type == "designation":
        if request.method == "POST":
            department = request.POST["department"]
            designation = request.POST.get("designation")
            start = request.POST.get("start_date")
            tomorrow = str(datetime.date.today() + datetime.timedelta(days=1))
            end = request.POST.get("end_date")
            if end:
                end = datetime.datetime.strptime(end, "%Y-%m-%d")
            else:
                end = datetime.datetime.strptime(tomorrow, "%Y-%m-%d")
            end = end + datetime.timedelta(days=1)
            if start:
                if designation:
                    job = JobRequisition.objects.filter(department=department, designation=designation,
                                                        edited_date__range=[start, end])
                else:
                    job = JobRequisition.objects.filter(department=department, edited_date__range=[start, end])
            else:
                if designation:
                    job = JobRequisition.objects.filter(department=department, designation=designation)
                else:
                    job = JobRequisition.objects.filter(department=department)

            data = {"job": job, "type": type, "number": number, "editaccess": edit_list}
            return render(request, "erf/export_table.html", data)
        else:
            messages.info(request, "Invalid Request. You have been logged out :)")
            return redirect("/erf/")
    else:
        messages.info(request, "Invalid Request. You have been logged out :)")
        return redirect("/erf/")


@login_required
def CreationApproval(request):
    if request.method == "POST":
        id = request.POST["id"]
        response = request.POST["response"]
        csrf = request.POST["csrfmiddlewaretoken"]
        if response == "Approve":
            request_status = "Pending"
        if response == "Reject":
            request_status = "Rejected by Manager"
        try:
            JobRequisition.objects.get(unique_id=csrf)
            messages.info(request, "Changes have been done please refresh the page!")
            if request.user.profile.emp_desi in hr_list:
                return redirect("/erf/hr-dashboard")
            elif request.user.profile.emp_desi in am_mgr_list:
                return redirect("/erf/manager-dashboard")
            else:
                messages.info(request, "Invalid Request. You have been logged out :)")
                return redirect("/erf/")
        except JobRequisition.DoesNotExist:
            e = JobRequisition.objects.get(id=id)
            a = Tickets.objects.get(job_requisition_id=id)
            e.unique_id = csrf
            if response == "Approve":
                e.ticket_status = True
                e.manager_approval = True
                e.request_status = request_status
                comment = "Approved by Manager"
                message = "The Requisition Approved Successfully!"
                action = "Approved the AM Employee Requisition"
            if response == "Reject":
                e.initial_status = False
                e.request_status = request_status
                comment = "Rejected by Manager"
                message = "The Requisition status have been made as Rejected"
                action = "Rejected the AM Employee Requisition"
            e.save()
            now_datetime = datetime.datetime.now().strftime('%b %d,%Y %H:%M:%S')
            edited_name = request.user.profile.emp_name
            edited_id = request.user.profile.emp_id
            edited_by = str([now_datetime, edited_name, edited_id, comment])
            previous = a.edited_by
            adding = previous + ",\n" + edited_by
            a.edited_by = adding
            a.save()
            messages.info(request, message)

            subject = action + " - Employee Requisition [" + str(e.id) + "]"
            html_path = 'erf/email.html'
            data = {'id': e.id, "created_date": e.edited_date, "hc": e.hc_req, "department": e.department,
                    "position": e.designation,
                    "deadline": e.dead_line, "campaign": e.campaign, "user": request.user.profile.emp_name,
                    "action": action, "status": e.request_status}
            email_template = get_template(html_path).render(data)
            creater_id = e.created_by_id
            creater_email = Profile.objects.get(emp_id=creater_id).emp_email
            manager_email = Profile.objects.get(emp_id=e.created_by_manager_id).emp_email
            to = [request.user.profile.emp_email, "ta@expertcallers.com","dina@expertcallers.com","joseph@expertcallers.com", creater_email, manager_email]
            email_msg = EmailMessage(subject,
                                     email_template, 'erf@expertcallers.com',
                                     to,
                                     reply_to=['erf@expertcallers.com'])
            email_msg.content_subtype = 'html'
            email_msg.send(fail_silently=False)
            if request.user.profile.emp_desi in hr_list:
                return redirect("/erf/hr-dashboard")
            elif request.user.profile.emp_desi in am_mgr_list:
                return redirect("/erf/manager-dashboard")
            else:
                messages.info(request, "Invalid Request. You have been logged out :)")
                return redirect("/erf/")
    else:
        messages.info(request, "Invalid Request. You have been logged out :)")
        return redirect("/erf/")

@login_required
def DeteleRequest(request, type):
    if type == "approve":
        if request.method == "POST":
            id = request.POST["id"]
            response = request.POST["response"]
            csrf = request.POST["csrfmiddlewaretoken"]
            try:
                JobRequisition.objects.get(unique_id=csrf)
                messages.info(request, "Changes have been done please refresh the page!")
                if request.user.profile.emp_desi in hr_list:
                    return redirect("/erf/hr-dashboard")
                elif request.user.profile.emp_desi in am_mgr_list:
                    return redirect("/erf/manager-dashboard")
                else:
                    messages.info(request, "Invalid Request. You have been logged out :)")
                    return redirect("/erf/")
            except JobRequisition.DoesNotExist:
                e = JobRequisition.objects.get(id=id)
                e.unique_id = csrf
                if response == "Approve":
                    e.ticket_status = False
                    e.request_status = "Deletion Approved by "+str(request.user.profile.emp_name)
                    comments = "Deletion Request Approved"
                    message = "Requisition Deleted Successfully!!"
                    action = "Approved Deletion Request"
                else:
                    e.ticket_status = True
                    e.deletion = False
                    e.request_status = "Deletion Rejected by "+str(request.user.profile.emp_name)
                    comments = "Deletion Request Rejected"
                    message = "Requisition Deletion Rejected"
                    action = "Rejected Deletion Request"
                e.save()

                a = Tickets.objects.get(job_requisition_id=id)
                now_datetime = datetime.datetime.now().strftime('%b %d,%Y %H:%M:%S')
                edited_name = request.user.profile.emp_name
                edited_id = request.user.profile.emp_id
                edited_by = str([now_datetime, edited_name, edited_id, comments])
                previous = a.edited_by
                adding = previous + ",\n" + edited_by
                a.edited_by = adding
                a.save()
                subject = action + " - Employee Requisition [" + str(e.id) +"]"
                html_path = 'erf/email.html'
                data = {'id': e.id, "created_date": e.edited_date, "hc": e.hc_req, "department": e.department,
                        "position": e.designation,
                        "deadline": e.dead_line, "campaign": e.campaign, "user": request.user.profile.emp_name,
                        "action": action, "status": e.request_status}
                email_template = get_template(html_path).render(data)
                creater_email = Profile.objects.get(emp_id=e.created_by_id).emp_email
                manager_email = Profile.objects.get(emp_id=e.created_by_manager_id).emp_email
                try:
                    rm1_email = Profile.objects.get(emp_id=e.created_by_rm1_id).emp_email
                except Profile.DoesNotExist:
                    rm1_email = creater_email
                to = [request.user.profile.emp_email, "ta@expertcallers.com","dina@expertcallers.com","joseph@expertcallers.com", creater_email, manager_email, rm1_email]
                email_msg = EmailMessage(subject,
                                         email_template, 'erf@expertcallers.com',
                                         to,
                                         reply_to=['erf@expertcallers.com'])
                email_msg.content_subtype = 'html'
                email_msg.send(fail_silently=False)
                messages.info(request, message)
                if request.user.profile.emp_desi in hr_list:
                    return redirect("/erf/hr-dashboard")
                elif request.user.profile.emp_desi in am_mgr_list:
                    return redirect("/erf/manager-dashboard")
                else:
                    messages.info(request, "Invalid Request. You have been logged out :)")
                    return redirect("/erf/")
        else:
            messages.info(request, "Invalid Request. You have been logged out :)")
            return redirect("/erf/")

    elif type == "request":
        if request.method == "POST":
            id = request.POST["id"]
            reason = request.POST["reason"]
            csrf = request.POST["csrfmiddlewaretoken"]
            try:
                JobRequisition.objects.get(unique_id=csrf)
                messages.info(request, "Changes have been done please refresh the page!")
                if request.user.profile.emp_desi in hr_list:
                    return redirect("/erf/hr-dashboard")
                elif request.user.profile.emp_desi in am_mgr_list:
                    return redirect("/erf/manager-dashboard")
                else:
                    messages.info(request, "Invalid Request. You have been logged out :)")
                    return redirect("/erf/")
            except JobRequisition.DoesNotExist:
                e = JobRequisition.objects.get(id=id)
                e.unique_id = csrf
                e.request_status = "Requested for Deletion"
                e.reason_for_deleting = reason
                e.deletion = True
                e.save()
                a = Tickets.objects.get(job_requisition_id=id)
                now_datetime = datetime.datetime.now().strftime('%b %d,%Y %H:%M:%S')
                edited_name = request.user.profile.emp_name
                edited_id = request.user.profile.emp_id
                edited_by = str([now_datetime, edited_name, edited_id, "Raised Deletion Request"])
                previous = a.edited_by
                adding = previous + ",\n" + edited_by
                a.edited_by = adding
                a.save()
                action = "Requested for Deletion"
                subject = action + " - Employee Requisition [" + str(e.id) +"]"
                html_path = 'erf/email.html'
                data = {'id': e.id, "created_date": e.edited_date, "hc": e.hc_req, "department": e.department,
                        "position": e.designation,
                        "deadline": e.dead_line, "campaign": e.campaign, "user": request.user.profile.emp_name,
                        "action": action, "status": e.request_status}
                email_template = get_template(html_path).render(data)
                creater_email = Profile.objects.get(emp_id=e.created_by_id).emp_email
                manager_email = Profile.objects.get(emp_id=e.created_by_manager_id).emp_email
                try:
                    rm1_email = Profile.objects.get(emp_id=e.created_by_rm1_id).emp_email
                except Profile.DoesNotExist:
                    rm1_email = creater_email
                to = [request.user.profile.emp_email, "ta@expertcallers.com","dina@expertcallers.com","joseph@expertcallers.com", creater_email, manager_email, rm1_email]
                email_msg = EmailMessage(subject,
                                         email_template, 'erf@expertcallers.com',
                                         to,
                                         reply_to=['erf@expertcallers.com'])
                email_msg.content_subtype = 'html'
                email_msg.send(fail_silently=False)
                messages.info(request, "Deletion Request Successful!")
                if request.user.profile.emp_desi in hr_list:
                    return redirect("/erf/hr-dashboard")
                elif request.user.profile.emp_desi in am_mgr_list:
                    return redirect("/erf/manager-dashboard")
                else:
                    messages.info(request, "Invalid Request. You have been logged out :)")
                    return redirect("/erf/")

        else:
            messages.info(request, "Invalid Request. You have been logged out :)")
            return redirect("/erf/")

def SendMail(request):
    id = request.POST["job"]
    emp_id = request.POST["emp_id"]
    newcampaign = request.POST["campaign"]
    oldcampaign = request.POST["oldcampaign"]
    send = request.POST["send"]
    name = AllAgents.objects.get(emp_id=emp_id).emp_name
    subject = "New Internal Movement"
    email_template = "Name: "+name+"<br> Emp ID: "+emp_id+"<br> Old Campaign: "+oldcampaign+"<br> New Campaign: "+newcampaign+"<br><br>"
    to = ["ta@expertcallers.com","dina@expertcallers.com","joseph@expertcallers.com"]
    email_msg = EmailMessage(subject,
                             email_template, 'erf@expertcallers.com',
                             to,
                             reply_to=['erf@expertcallers.com'])
    email_msg.content_subtype = 'html'
    email_msg.send(fail_silently=False)

    job = JobRequisition.objects.get(id=id)
    if send == "send_mail_1":
        job.send_mail_1 = True
        job.source_internal_emp_id_1 = emp_id
        job.source_internal_emp_name_1 = name
        job.source_internal_campaign_name_1 = oldcampaign
    if send == "send_mail_2":
        job.send_mail_2 = True
        job.source_internal_emp_id_2 = emp_id
        job.source_internal_emp_name_2 = name
        job.source_internal_campaign_name_2 = oldcampaign
    if send == "send_mail_3":
        job.send_mail_3 = True
        job.source_internal_emp_id_3 = emp_id
        job.source_internal_emp_name_3 = name
        job.source_internal_campaign_name_3 = oldcampaign
    if send == "send_mail_4":
        job.send_mail_4 = True
        job.source_internal_emp_id_4 = emp_id
        job.source_internal_emp_name_4 = name
        job.source_internal_campaign_name_4 = oldcampaign
    if send == "send_mail_5":
        job.send_mail_5 = True
        job.source_internal_emp_id_5 = emp_id
        job.source_internal_emp_name_5 = name
        job.source_internal_campaign_name_5 = oldcampaign
    if send == "send_mail_6":
        job.send_mail_6 = True
        job.source_internal_emp_id_6 = emp_id
        job.source_internal_emp_name_6 = name
        job.source_internal_campaign_name_6 = oldcampaign
    if send == "send_mail_7":
        job.send_mail_7 = True
        job.source_internal_emp_id_7 = emp_id
        job.source_internal_emp_name_7 = name
        job.source_internal_campaign_name_7 = oldcampaign
    if send == "send_mail_8":
        job.send_mail_8 = True
        job.source_internal_emp_id_8 = emp_id
        job.source_internal_emp_name_8 = name
        job.source_internal_campaign_name_8 = oldcampaign
    if send == "send_mail_9":
        job.send_mail_9 = True
        job.source_internal_emp_id_9 = emp_id
        job.source_internal_emp_name_9 = name
        job.source_internal_campaign_name_9 = oldcampaign
    if send == "send_mail_10":
        job.send_mail_10 = True
        job.source_internal_emp_id_10 = emp_id
        job.source_internal_emp_name_10 = name
        job.source_internal_campaign_name_10 = oldcampaign
    if send == "send_mail_11":
        job.send_mail_11 = True
        job.source_internal_emp_id_11 = emp_id
        job.source_internal_emp_name_11 = name
        job.source_internal_campaign_name_11 = oldcampaign
    if send == "send_mail_12":
        job.send_mail_12 = True
        job.source_internal_emp_id_12 = emp_id
        job.source_internal_emp_name_12 = name
        job.source_internal_campaign_name_12 = oldcampaign
    if send == "send_mail_13":
        job.send_mail_13 = True
        job.source_internal_emp_id_13 = emp_id
        job.source_internal_emp_name_13 = name
        job.source_internal_campaign_name_13 = oldcampaign
    if send == "send_mail_14":
        job.send_mail_14 = True
        job.source_internal_emp_id_14 = emp_id
        job.source_internal_emp_name_14 = name
        job.source_internal_campaign_name_14 = oldcampaign
    if send == "send_mail_15":
        job.send_mail_15 = True
        job.source_internal_emp_id_15 = emp_id
        job.source_internal_emp_name_15 = name
        job.source_internal_campaign_name_15 = oldcampaign
    if send == "send_mail_16":
        job.send_mail_16 = True
        job.source_internal_emp_id_16 = emp_id
        job.source_internal_emp_name_16 = name
        job.source_internal_campaign_name_16 = oldcampaign
    if send == "send_mail_17":
        job.send_mail_17 = True
        job.source_internal_emp_id_17 = emp_id
        job.source_internal_emp_name_17 = name
        job.source_internal_campaign_name_17 = oldcampaign
    if send == "send_mail_18":
        job.send_mail_18 = True
        job.source_internal_emp_id_18 = emp_id
        job.source_internal_emp_name_18 = name
        job.source_internal_campaign_name_18 = oldcampaign
    if send == "send_mail_19":
        job.send_mail_19 = True
        job.source_internal_emp_id_19 = emp_id
        job.source_internal_emp_name_19 = name
        job.source_internal_campaign_name_19 = oldcampaign
    if send == "send_mail_20":
        job.send_mail_20 = True
        job.source_internal_emp_id_20 = emp_id
        job.source_internal_emp_name_20 = name
        job.source_internal_campaign_name_20 = oldcampaign
    job.save()
    return HttpResponse("Mail Sent to CC Team Successfully!")