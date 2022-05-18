
from apscheduler.schedulers.background import BackgroundScheduler
from .jobs import schedule_task

def start():

    scheduler = BackgroundScheduler()
    # scheduler.add_job(schedule_task,'cron',month ='*', day = '17',hour = '13')
    scheduler.add_job(schedule_task,'interval',seconds = 5)
    scheduler.start()
    