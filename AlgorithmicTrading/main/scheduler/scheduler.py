from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events
from django.utils import timezone
from django_apscheduler.models import DjangoJobExecution
import sys

from .emails import send_email
from ..models import Signup

# This is the function you want to schedule - add as many as you want and then register them in the start() function below
def send_all_emails():
    all_signups = Signup.objects.all()
    for signup in all_signups:
        send_email(signup.email, signup.ticker, signup.strategy)
    
def start():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")
    #run send_all_emails once a day
    scheduler.add_job(send_all_emails, 'interval', minutes=1440, name='send_all_emails', jobstore='default')
    register_events(scheduler)
    scheduler.start()
    print("Scheduler started...", file=sys.stdout)