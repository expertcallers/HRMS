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
    path('',loginPage),
    path('login',loginAndRedirect),
    path('logout',logoutView),
    path('dashboard-redirect/<int:id>',redirectTOAllDashBoards),
    path('change-password',change_password),
    path('team-dashboard',teamDashboard),
    path('index',indexPage),
    path('employee-details/<int:pk>',employeeDetails),
    path('agent-dashboard',agentDashBoard),
    path('ams-update-attendance',newSingleAttandance),
    path('tl-dashboard',tlDashboard),
    path('hr-dashboard',hrDashboard),
    path('add-new-user',addNewUserHR),
    path('viewusers',viewUsersHR),
    path('onboarding',onboardingHR),

    path('apply-attendance',applyAttendace),
    path('team-attendance',teamAttendance),

    path('rm-approval/<int:id>',rmApproval),
    path('view-att-requests',attRequests),
    path('ams-agent-settings',agentSettings),
    path('rm-settings',rmSettings),
    path('upload-image',uploadImageToDB),

    # Mapping

    path('rm-mapping-index',mappingHomePage),
    path('create-mapping-ticket',createMappingTicket),
    path('view-mapping-tickets',viewMappingTicketsHr),
    path('approve-mapping-ticket',approveMappingTicket),

    path('add-new-job',jobRequisition),




]
