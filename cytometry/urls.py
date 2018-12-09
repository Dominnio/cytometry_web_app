from django.urls import path
from django.conf.urls import url, include

from . import views

app_name = 'cytometry'
urlpatterns = [
    path('file/', views.show_file, name='show_file'),
    path('form_step_0/', views.start, name='start'),
    path('form_step_1/', views.upload_file, name='upload_file'),
    path('form_step_2/', views.run, name='run'),
    path('form_step_3/', views.result, name='result'),
    path('form_step_4/', views.show, name='show'),
    url(r'^$', views.perform,name='perform'),
    url(r'^process_state$', views.process_state,name='process_state'),
]
