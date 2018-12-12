from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.template import loader
from django.http import Http404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.contrib import messages
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings
from .models import Document
from mysite.celery import app
from celery import shared_task,current_task
from celery import task
from celery.result import AsyncResult
import os.path
import glob
import json
from cytometry import grouping
from .tasks import kmeans
from . import forms
from . import tasks
import matplotlib.pyplot as plt, mpld3

'''
show() gets chart parameter, create chart, optionally save it to file (if it's 3 dimensonal graf), and render 
'''
def show(request):
    flag = False
    dim_1 = -1
    dim_2 = -1
    dim_3 = -1
    if('pca' in request.POST):
        flag = True
    dim = request.POST['dim']
    if(flag != True):
        dim_1 = request.POST['first_dim']
        if(int(dim) == 2):        
            dim_2 = request.POST['second_dim']
        if(int(dim) == 3):
            dim_2 = request.POST['second_dim']
            dim_3 = request.POST['third_dim']
    name = request.POST['file_name']
    path_file = settings.MEDIA_ROOT +  '/' +  name
    form = forms.MyForm(path_file)
    result = forms.ResultForm(name)
    fig = grouping.image_create(dim, flag, dim_1, dim_2, dim_3, path_file, name)
    if(int(dim) == 3):
        return render(request, 'cytometry/form_step_3.html', {'form': form, 'name': name, 'unknown_k': 1, 'img' : 1, 'result': result})
    return render(request, 'cytometry/form_step_3.html', {'form': form, 'name': name, 'unknown_k': 1, 'img' : 1, 'result': result })#, 'fig': [fig]})

'''
result() shows cluster parameter
'''
def result(request):
    name = request.POST['file_name']
    path_file = settings.MEDIA_ROOT + '/' +  name
    result = forms.ResultForm(name)
    form = forms.MyForm(path_file)
    return render(request, 'cytometry/form_step_3.html', {'form': form, 'name': name, 'result': result, 'unknown_k': 1})

'''
process_state() shows current task progress bar (update it)
'''
def process_state(request, job_id, name):
    """ A view to report the progress to the user """
    data = 'Fail'
    if request.is_ajax():
        task_id = job_id
        task = AsyncResult(task_id)
        data = task.result or task.state
    else:
        data = 'This is not an ajax request'

    json_data = json.dumps(data)
    return HttpResponse(json_data, content_type='application/json')

'''
perform() shows progress bar
'''
def perform(request, job_id, name):
    job = AsyncResult(job_id)
    data = job.result or job.state
    context = {
        'data':data,
        'task_id':job_id,
        'name':name,
    }
    return render(request,"cytometry/form_step_2.html",context)

'''
run() gets all parameters to the algorithm from POST:
    0. file name
    1. type of algorithm
    2. parameters
    3. evaluations type
then run() start task
next render site with form (because we must know dimension names)
TODO : shoud get type of algorithm, and do diffrent things depend on it
'''
def run(request):
    name = request.POST['file_name']
    path_file = settings.MEDIA_ROOT + '/' +  name

    checks = request.POST.getlist('checks[]')
    if('n_clusters_unknown' in request.POST):
        n_clusters = 0
        from_val = int(request.POST['from'])
        to_val = int(request.POST['to'])    
    else:
        n_clusters = int(request.POST['n_clusters'])
        from_val = 0
        to_val = 0
    n_init = int(request.POST['n_init'])
    max_iter = int(request.POST['max_iter'])
    tol = float(request.POST['tol'])
    if('preprocessing' in request.POST):
        preprocessing = True
    else:
        preprocessing = False
    form = forms.MyForm(path_file)
    job = kmeans.delay(path_file, n_clusters, n_init, max_iter, tol, from_val, to_val, checks, name, preprocessing)
    return HttpResponseRedirect('/job/' + job.id + '/' + name)

'''
show_file() show file in new site
'''
def show_file(request):
    file_name = request.GET['file']
    data = forms.SamplesForm(file_name)
    return render(request, 'cytometry/file.html', {'data': data})

'''
upload_file() is run  if we get POST from upload button
in these case add uploaded file to media directory and render next site
'''
def upload_file(request):
    if 'task_id' in request.POST:
        task_id = request.POST['task_id']
        name = request.POST['f_name']
        app.control.revoke(task_id, terminate=True)
        return render(request, 'cytometry/form_step_1.html', {'name': name})
    documents = Document.objects.all()
    form = forms.DocumentForm(request.POST, request.FILES)
    if form.is_valid():
        newdoc = Document(docfile = request.FILES['docfile'])
        name = newdoc.__unicode__()
        if('[' in name or ']' in name or '/' in name or '.fcs' not in name or len(name) <= 4):
            form = forms.DocumentForm()
            return render(request, 'cytometry/form_step_0.html', {'form': form, 'wrong_file': 1})
        ext = name.split('.')[-1]
        if(ext != 'fcs'):
            form = forms.DocumentForm()
            return render(request, 'cytometry/form_step_0.html', {'form': form, 'wrong_file': 1})
        if(newdoc.docfile.file.size > 10485760):
            return render(request, 'cytometry/form_step_0.html', {'form': form, 'too_big': 1})
        newdoc.save()
        document = newdoc
        name = newdoc.__unicode__()
        messages.info(request, 'File uploaded successfully!')
        return render(request, 'cytometry/form_step_1.html', {'name': name})

'''
not used yet at all
'''
def close(request):
    name = request.GET['name']
    if os.path.isfile(settings.MEDIA_ROOT + '/' + name):
        os.remove(settings.MEDIA_ROOT + '/' + name)
        os.remove(settings.MEDIA_ROOT + '/result_centers_' + name + '.txt')
        os.remove(settings.MEDIA_ROOT + '/result_labels_' + name + '.txt')
    if os.path.isfile(settings.BASE_DIR  + '/cytometry/static/real_data_result_' + name + '.png'):
        os.remove(settings.BASE_DIR  + '/cytometry/static/real_data_result_' + name + '.png')

'''
start() is run  if we visit site first time
'''
def start(request):
    form = forms.DocumentForm()
    return render(request, 'cytometry/form_step_0.html', {'form': form})
