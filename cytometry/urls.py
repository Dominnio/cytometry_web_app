from django.urls import path
from django.conf.urls import url, include

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
    url(r'^close$', views.close,name='close'),
]
