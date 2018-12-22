'''

Autor:    		Dominik Orliński 
Prawa autorskie:  	(c) Dominik Orliński 
Data:    		1.01.2019 
Wersja:   		1.0

'''

from django.urls 	import path
from django.conf.urls 	import url, include

from . import views

app_name = 'cytometry'
urlpatterns = [
    path('file/', views.show_file, name='show_file'),
    path('', views.start, name='start'),
    path('step_1/', views.upload_file, name='upload_file'),
    path('step_2/', views.run, name='run'),
    path('step_3/', views.result, name='result'),
    path('step_4/', views.show, name='show'),
    path('job/<job_id>/<name>/', views.perform,name='perform'),
    path('job/<job_id>/<name>/process_state/', views.process_state,name='process_state'),
    path('iamhere/', views.iamhere, name='iamhere'),
    path('download/', views.download_file, name='download'),
]

