from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from .jobs import schedule_task,scheduleAddCalander


def startfun():
    scheduler = BackgroundScheduler()
    scheduler.add_job(scheduleAddCalander,'cron',month ='*', day = '17',hour = '17', minute = '10', second = '1')
    scheduler.start()

