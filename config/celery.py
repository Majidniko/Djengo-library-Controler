import os
from celery import Celery
from celery.schedules import crontab


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'check-overdue-books-every-6-hours': {
        'task': 'books.tasks.check_overdue_books',
        #'schedule': crontab(minute=0, hour='*/6'),  # هر ۶ ساعت
        'schedule': 30, 

    },
}