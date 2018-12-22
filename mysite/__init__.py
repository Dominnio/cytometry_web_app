'''

Autor:    		Dominik Orliński 
Prawa autorskie:  	(c) Dominik Orliński 
Data:    		1.01.2019 
Wersja:   		1.0

'''

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from .celery import app as celery_app

#__all__ = ('celery_app',)
