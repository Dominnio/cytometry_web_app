from django.urls import path
from django.conf.urls import url, include

from . import views

app_name = 'cytometry'
urlpatterns = [
    path('form/', views.upload_file, name='upload_file'),
    path('launched/', views.run, name='run'),
    path('result/', views.show, name='show'),
    url(r'^$', views.index,name='index'),
    url(r'^poll_state$', views.poll_state,name='poll_state'),
]
