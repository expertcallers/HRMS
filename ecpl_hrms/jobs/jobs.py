from django.conf import settings
from ams import views

def schedule_task():
    views.schedule_print()


    