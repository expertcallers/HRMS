from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, update_session_auth_hash, authenticate
from django.contrib.auth.forms import PasswordChangeForm
from .models import *
from django.apps import apps

manager_list = ['TA Manager', 'Operations Manager', 'IT Manager', 'Associate Director', 'Vice President',
                'Learning and Development Head', 'Chief Compliance Officer', 'Chief Executive Officer',
                'Managing Director', 'HR Manager', 'Board member', 'Command Centre Head', 'Chief Technology Officer']

Profile = apps.get_model('mapping', 'Profile')
Designation = apps.get_model('ams', 'Designation')


def view_404(request, exception=None):
    return render(request, 'pbi/404.html')


# Management Dashboard
@login_required
def managementDashboard(request):
    try:
        campaignid = request.user.campaign.campaignid
        campaign_type = request.user.campaign.campaign_type
        if campaignid == 'all':
            if campaign_type == 'limited':
                cam_id = []
                mapping = Mapping.objects.filter(user=request.user)
                for i in mapping:
                    cam_id.append(i.campaign.campaignid)
                all_cam = Campaign.objects.filter(campaignid__in=cam_id).exclude(
                    Q(campaign_type=None) | Q(campaign_type='limited')).count()
            else:
                all_cam = Campaign.objects.exclude(Q(campaign_type=None) | Q(campaign_type='limited')).count()

            if campaign_type == 'limited':
                cam_id = []
                mapping = Mapping.objects.filter(user=request.user)
                for i in mapping:
                    cam_id.append(i.campaign.campaignid)
                outbound = Campaign.objects.filter(campaignid__in=cam_id, campaign_type="Outbound").count()
            else:
                outbound = Campaign.objects.filter(campaign_type="Outbound").count()

            if campaign_type == 'limited':
                cam_id = []
                mapping = Mapping.objects.filter(user=request.user)
                for i in mapping:
                    cam_id.append(i.campaign.campaignid)
                inbound = Campaign.objects.filter(campaignid__in=cam_id, campaign_type="Inbound").count()
            else:
                inbound = Campaign.objects.filter(campaign_type="Inbound").count()

            if campaign_type == 'limited':
                cam_id = []
                mapping = Mapping.objects.filter(user=request.user)
                for i in mapping:
                    cam_id.append(i.campaign.campaignid)
                email = Campaign.objects.filter(campaignid__in=cam_id, campaign_type="Email").count()
            else:
                email = Campaign.objects.filter(campaign_type="Email").count()

            if campaign_type == 'limited':
                cam_id = []
                mapping = Mapping.objects.filter(user=request.user)
                for i in mapping:
                    cam_id.append(i.campaign.campaignid)
                other = Campaign.objects.filter(campaignid__in=cam_id, campaign_type="Other").count()
            else:
                other = Campaign.objects.filter(campaign_type="Other").count()

            data = {"all": all_cam, "outbound": outbound, "inbound": inbound, "email": email, "other": other}
            return render(request, 'pbi/management_dashboard.html', data)
        else:
            messages.info(request, "Bad Request.")
            return redirect('/pbireport/')
    except:
        messages.info(request, "Bad Request.")
        return redirect('/ams/dashboard-redirect')


@login_required
def campaignsReport(request, type):
    try:
        campaignid = request.user.campaign.campaignid
        campaign_type = request.user.campaign.campaign_type
        if campaignid == 'all':
            if type == "all":
                if campaign_type == 'limited':
                    cam_id = []
                    mapping = Mapping.objects.filter(user=request.user)
                    for i in mapping:
                        cam_id.append(i.campaign.campaignid)
                    pro = Campaign.objects.filter(campaignid__in=cam_id).exclude(
                        Q(campaign_type=None) | Q(campaign_type='limited'))
                else:
                    pro = Campaign.objects.exclude(Q(campaign_type=None) | Q(campaign_type='limited'))
            else:
                if campaign_type == 'limited':
                    cam_id = []
                    mapping = Mapping.objects.filter(user=request.user)
                    for i in mapping:
                        cam_id.append(i.campaign.campaignid)
                    pro = Campaign.objects.filter(campaign_type=type, campaignid__in=cam_id).exclude(campaign_type=None)
                else:
                    pro = Campaign.objects.filter(campaign_type=type)
            data = {'campaign': pro, "type": type}
            return render(request, 'pbi/reports_all.html', data)
        else:
            messages.info(request, "Bad Request!")
            return redirect('/pbireport/')
    except:
        messages.info(request, "Bad Request.")
        return redirect('/pbireport/')


@login_required
def allReport(request, cid):
    try:
        campaignid = request.user.campaign.campaignid
        campaign_type = request.user.campaign.campaign_type
        if campaignid == cid or campaignid == 'all':
            campaign = Campaign.objects.get(campaignid=cid)
            try:
                link = CampaignLinks.objects.get(campaign=campaign).link
            except CampaignLinks.DoesNotExist:
                messages.info(request, 'Link Not yet assigned to Campaign. Contact Sindhu from CC Team!')
                return redirect('/pbireport/management-dashboard')
            data = {'link': link, 'campaign': campaign}
            if request.user.campaign.campaign_status == False:
                messages.info(request, "The Campaign is currently paused")
                return redirect('/pbireport/')
            elif campaign_type == 'limited':
                cam_id = []
                mapping = Mapping.objects.filter(user=request.user)
                for i in mapping:
                    cam_id.append(i.campaign.campaignid)
                if cid in cam_id:
                    return render(request, 'pbi/single_report.html', data)
                else:
                    messages.info(request, "Bad Request!")
                    return redirect('/pbireport/')
            else:
                return render(request, 'pbi/single_report.html', data)
        else:
            messages.info(request, "Bad Request!")
            return redirect('/pbireport/')
    except:
        messages.info(request, "Bad Request.")
        return redirect('/pbireport/')


@login_required
def campaignAssigning(request):
    try:
        if request.user.campaign.campaign_type == None:
            if request.method == "POST":
                user = request.POST['user']
                user = User.objects.get(username=user)
                campaign = request.POST['campaign']
                campaign = Campaign.objects.get(campaignid=campaign)
                Mapping.objects.create(user=user, campaign=campaign)
                return redirect('/pbireport/campaign-assigning')

            else:
                campaigns = Campaign.objects.exclude(Q(campaign_type=None) | Q(campaign_type='limited'))
                profiles = Campaign.objects.filter(Q(campaign_type='limited'))
                mapping = Mapping.objects.all()
                mapping_list = []
                for i in mapping:
                    dic = {}
                    campaign = Campaign.objects.get(user=i.user)
                    dic['user'] = campaign.campaign + " (" + str(i.user) + ")"
                    dic['campaign'] = i.campaign
                    dic['id'] = i.id
                    mapping_list.append(dic)
                data = {'campaigns': campaigns, 'profiles': profiles, 'mapping': mapping_list}
                return render(request, 'pbi/superadmin/campaign_assigning.html', data)
        else:
            messages.info(request, "Bad Request!")
            return redirect('/pbireport/')
    except:
        messages.info(request, "Bad Request.")
        return redirect('/pbireport/')


@login_required
def deleteMapping(request):
    if request.method == "POST":
        id = request.POST['id']
        Mapping.objects.get(id=id).delete()
        return redirect('/pbireport/campaign-assigning')
    else:
        messages.info(request, "Bad Request!")
        return redirect('/pbireport/')


def createUsers(request):
    emp_desi = []
    category = ['TL AM', 'TL AM HR', 'TA - TL - AM', 'OM HR', 'Manager List', 'Management List - HR', 'Management List',
                'HR']
    for i in Designation.objects.filter(category__in=category):
        emp_desi.append(i.name)
    employees = Profile.objects.filter(emp_desi__in=emp_desi).exclude(
        agent_status__in=['Attrition', 'Attrition Duplicate'])
    for i in employees:
        user = User.objects.filter(username=i.emp_id)
        if user.exists():
            try:
                for j in user:
                    user = j
                Campaign.objects.get(user=user)
            except:
                if i.emp_desi in manager_list:
                    Campaign.objects.create(
                        user=user, campaign=i.emp_name, campaignid='all',
                    )
                else:
                    Campaign.objects.create(
                        user=user, campaign=i.emp_name, campaignid='all', campaign_type='limited',
                    )
        else:
            user = User.objects.create_user(username=i.emp_id, password=str(i.emp_id))
            if i.emp_desi in manager_list:
                Campaign.objects.create(
                    user=user, campaign=i.emp_name, campaignid='all',
                )
            else:
                Campaign.objects.create(
                    user=user, campaign=i.emp_name, campaignid='all', campaign_type='limited',
                )
    return redirect('/')
