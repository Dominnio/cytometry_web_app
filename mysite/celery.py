'''

Autor:    		Dominik Orliński 
Prawa autorskie:  	(c) Dominik Orliński 
Data:    		1.01.2019 
Wersja:   		1.0

Plik konfiguracyjny dla kolejki zadań Celery. 

'''

from __future__ 	import absolute_import
from django.conf 	import settings
from celery 		import Celery
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')

app = Celery('mysite', backend='amqp', broker='amqp://guest@localhost//')

app.config_from_object('django.conf:settings')

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

@app.task(bind=True)
def debug_task(self):
    print("Request: {0!r}".format(self.request))
