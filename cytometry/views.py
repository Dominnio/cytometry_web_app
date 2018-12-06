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
from celery import shared_task,current_task
from celery import task
from celery.result import AsyncResult
import os.path
import glob
import json
from cytometry import grouping
from .tasks import add,fft_random
#from .forms import DocumentForm, MyForm
#from .forms import UserForm
#from .tasks import add,fft_random

from . import forms
from . import tasks

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

def poll_state(request):
    """ A view to report the progress to the user """
    data = 'Fail'
    if request.is_ajax():
        if 'task_id' in request.POST.keys() and request.POST['task_id']:
            task_id = request.POST['task_id']
            task = AsyncResult(task_id)
            data = task.result or task.state
        else:
            data = 'No task_id in the request'
    else:
        data = 'This is not an ajax request'

    json_data = json.dumps(data)
    return HttpResponse(json_data, content_type='application/json')

def index(request):
    if 'job' in request.GET:
        job_id = request.GET['job']
        job = AsyncResult(job_id)
        data = job.result or job.state
        context = {
            'data':data,
            'task_id':job_id,
        }
        return render(request,"show_t.html",context)
    elif 'n' in request.GET:
        n = request.GET['n']
        job = fft_random.delay(int(n))
        return HttpResponseRedirect('/cytometry/' + '?job=' + job.id)
    else:
        form = forms.UserForm()
        context = {
            'form':form,
        }
        return render(request,"post_form.html",context)

def run(request):
	name = request.POST.getlist('option[]')
	split = name[0].split(']')
	name = split[0]
	path_file = settings.MEDIA_ROOT +  '/' + 'documents' + '/' +  name

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
	form = forms.MyForm(path_file)

	grouping.kmeans(path_file, n_clusters, n_init, max_iter, tol, from_val, to_val, checks)
	return render(request, 'cytometry/form.html',  {'form': form, 'name': name, 'step' : 2})
'''
show() gets chart parameter, create chart, save it to file, and render 
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

	name = request.POST.getlist('option[]')
	print(name)
	path_file = settings.MEDIA_ROOT +  '/' + 'documents' + '/' +  name[0]

	grouping.image_create(dim, flag, dim_1, dim_2, dim_3,path_file)
	return render(request, 'cytometry/result.html')


'''
upload_file() is run 
	1. when site is visited first time 
	2. if we get POST from upload button
	3. if someone refresh form (send POST agian)

is these cases we do
	1. render site only with form (step 0)
	2. add uploaded file to media directory, render site with file name (step 1)
	3. same as above, but previously displays an alert 

TODO : should check file name, wheather it have / or [] or is not fcs or is too big
'''
def upload_file(request):
	documents = Document.objects.all()
	if request.method == 'POST':
		form = forms.DocumentForm(request.POST, request.FILES)
		if form.is_valid():
			newdoc = Document(docfile = request.FILES['docfile'])
			newdoc.save()
			name = newdoc.__unicode__()
			split = name.split('/')
			name = split[1]
			document = newdoc
			messages.info(request, 'File uploaded successfully!')
			return render(request, 'cytometry/form.html', {'name': name, 'step' : 1})
	else:
		form = forms.DocumentForm()
		return render(request, 'cytometry/form.html', {'form': form, 'step' : 0})
