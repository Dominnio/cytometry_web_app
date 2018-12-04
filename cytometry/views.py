from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.template import loader
from django.http import Http404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.contrib import messages
from .models import Document
from django.shortcuts import render_to_response
from django.template import RequestContext
import os.path
from cytometry import grouping
from .forms import DocumentForm, MyForm
from django.conf import settings
import glob
from celery import shared_task,current_task
from celery import task

def run(request):
    if(not ('option[]' in request.POST)):
        documents = Document.objects.all()
        form = DocumentForm(request.POST, request.FILES)
        return render(request, 'cytometry/form.html', {'documents': documents, 'form': form})
    opt = request.POST.getlist('option[]')
    split = opt[0].split('/')
    path_file = settings.MEDIA_ROOT +  '/' + split[2] + '/' +  split[3]
    if('n_clusters_unknown' in request.POST):
        n_clusters = 0
        f = int(request.POST['from'])
        t = int(request.POST['to'])	
    else:
        n_clusters = int(request.POST['n_clusters'])
        f = 0
        t = 0
    n_init = int(request.POST['n_init'])
    max_iter = int(request.POST['max_iter'])
    tol = float(request.POST['tol'])
    grouping.kmeans(path_file, n_clusters, n_init, max_iter, tol, f, t)
    form = MyForm(path_file)

    return render(request, 'cytometry/launched.html', {'form' : form})

def calculate(request):
    checks = request.POST.getlist('checks[]')
    grouping.validate(checks)
    return render(request, 'cytometry/evaluation.html')

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
    grouping.image_create(dim, flag, dim_1, dim_2, dim_3)
    return render(request, 'cytometry/result.html')

def upload_file(request):
    documents = Document.objects.all()
    for document in documents:
    	document.delete()
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            newdoc = Document(docfile = request.FILES['docfile'])
            newdoc.save()
            name = newdoc.__unicode__()
            document = newdoc
            messages.info(request, 'File uploaded successfully!')
            return render(request, 'cytometry/form.html', {'document': document, 'name': name})
    else:
        form = DocumentForm()
        return render(request, 'cytometry/form.html', {'documents': documents, 'form': form})

# Create your views here.
