
from apscheduler.schedulers.background import BackgroundScheduler
from .jobs import schedule_task,scheduleAddCalander

<<<<<<< HEAD
def start():
=======

def startfun():
    scheduler = BackgroundScheduler()
    scheduler.add_job(scheduleAddCalander,'cron',month ='*', day = '17',hour = '17', minute = '10', second = '1')
    scheduler.start()
>>>>>>> fdef68b98bb6810d41aee2e0db55913c6c1b228f

    scheduler = BackgroundScheduler()
    # scheduler.add_job(schedule_task,'cron',month ='*', day = '17',hour = '13')
    scheduler.add_job(schedule_task,'interval',seconds = 5)
    scheduler.start()
    