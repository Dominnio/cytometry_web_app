from django.urls import path

from . import views

app_name = 'cytometry'
urlpatterns = [
    path('form/', views.upload_file, name='upload_file'),
    path('launched/', views.run, name='run'),
    path('result/', views.show, name='show'),
    path('evaluation/', views.calculate, name='calculate'),
]
