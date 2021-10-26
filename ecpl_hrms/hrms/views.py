from django.shortcuts import render

# Create your views here.
def indexHrms(request):
    return render(request,'hrms/hrms-home.html')
