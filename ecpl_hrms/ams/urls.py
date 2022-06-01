"""ecpl_hrms URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from .views import *

urlpatterns = [
    # Login
    path('', loginPage),
    path('login/', loginAndRedirect),
    path('login', loginAndRedirect),
    path('logout', logoutView),
    path('change-password', change_password),
    path('upload-image', uploadImageToDB),
    path('ams-agent-settings', agentSettings),
    path('rm-settings', rmSettings),
    path('edit-employee-profile-status', editAgentStatus),

    # Dashboard Redirect
    path('dashboard-redirect/<int:id>', redirectTOAllDashBoards),
    path('agent-dashboard', agentDashBoard),
    path('tl-dashboard', tlDashboard),
    path('manager-dashboard', managerDashboard),
    path('hr-dashboard', hrDashboard),

    # Attendance
    path('ams-update-attendance', newSingleAttandance),
    path('apply-attendance', applyAttendace),
    path('team-attendance', teamAttendance),
    path('view-emp-attendance', viewTeamAttendance),
    path('team-attendance-report', teamAttendanceReport),

    # Attendance Correction
    path('attendance-correction', attendanceCorrection),
    path('apply-attendance-correction', applyCorrection),
    path('approve-att-correction-req', approveAttendanceRequest),
    path('week-attendance', weekAttendanceReport),

    # User Managfement, Onboarding
    path('add-new-user', addNewUserHR),
    path('viewusers', viewUsersHR),
    path('view-employee-profile/<int:id>/<str:on_id>', viewEmployeeProfile),
    path('onboarding', on_boarding),
    path('view-onboarding', viewOnBoarding),
    path('edit-onboarding/<int:id>', on_boarding_update),
    path('bulk-onboarding', onboardingBulkUpload),
    path('view-all-employees-oms/<str:name>', viewallOMS),

    # Team Management
    path('add-newteam', addNewTeam),
    path('view-all-teams', viewTeam),

    # Leave Management
    path('ams-apply_leave', applyLeave),
    path('view-leave-list', viewleaveListRM1),
    path('approve-leave-rm1', approveLeaveRM1),
    path('view-leave-request-mgr', viewAndApproveLeaveRequestMgr),
    path('sl-proof', SLProofSubmit),
    path('apply-escalation', applyEscalation),
    path('view-leave-escalation-mgr', viewEscalation),
    path('leave-history', viewLeaveHistory),

    # Mapping
    path('rm-mapping-index', mappingHomePage),
    path('create-mapping-ticket', createMappingTicket),
    path('view-mapping-tickets', viewMappingTicketsHr),
    path('approve-mapping-ticket', approveMappingTicket),
    path('mapping-application-status', viewMappingApplicationStatus),

    path('change-emp-password', changeEmpPassword),
    path('add-new-designation', addNewDesi),
    path('test', TestFun),

    path('add-leave-balance/<str:a>', addLeaveBalance),
    path('auto-approve-leave', autoApproveLeave),
    path('add-attendance', addAttendance),
    path('sandwich', sandwichPolicy),
    path('maternity-leave', maternityLeave),

    path('ML',maternityleave),

]
