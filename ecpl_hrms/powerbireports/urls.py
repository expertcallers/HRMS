from django.urls import path
from .views import *

urlpatterns = [
    path('', managementDashboard),
    path('management-dashboard', managementDashboard),
    path('campaigns/<str:type>', campaignsReport),
    path('report/<str:cid>', allReport),
    path('management', managementDashboard),

    path('campaign-assigning', campaignAssigning),
    path('delete-mapping', deleteMapping),
    path('create-users', createUsers),
]