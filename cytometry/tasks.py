from celery import shared_task,current_task,task
from numpy import random
from scipy.fftpack import fft

import imp
import FlowCal
import gi
import time
import os
import time
import pandas as pd
import numpy as np
import glob
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn import preprocessing
from sklearn.decomposition import PCA
from sklearn.metrics import calinski_harabaz_score
from sklearn.metrics import davies_bouldin_score
from sklearn.metrics import silhouette_score
from scipy.spatial.distance import cdist, pdist
from django.conf import settings

def determine_number_of_clusters(samples,f,t, n_init, max_iter, tol, _file_path):
	calinski_choose = 0
	calinski_best = 0
	for i in range(f,t):
		progress = 90 * float(i-f) / float(t-f)
		samples = preprocessing.scale(samples, axis=0)
		kmenas = KMeans(i,n_init=n_init,max_iter=max_iter,tol=tol).fit(samples)
		calinski = calinski_harabaz_score(samples,kmenas.labels_)
		current_task.update_state(state='PROGRESS', meta={'process_percent': progress})
		if(calinski > calinski_best):
			calinski_choose = i
			calinski_best = calinski

	current_task.update_state(state='PROGRESS', meta={'process_percent': 99})

	return calinski_choose

@shared_task
def kmeans(file_path, n_clusters, n_init, max_iter, tol, from_val, to_val, checks, name): 
	current_task.update_state(state='PROGRESS', meta={'process_percent': 0})
	fcs_data = FlowCal.io.FCSData(file_path)
	samples = np.array(fcs_data, float)
	if(n_clusters == 0):
		n_clusters = determine_number_of_clusters(samples, from_val, to_val, n_init, max_iter, tol, file_path)
	samples = preprocessing.scale(samples, axis=0)
	kmeans = KMeans(n_clusters=n_clusters, n_init=n_init, max_iter=max_iter, tol=tol).fit(samples)

	i = 0
	text = ""
	for check in checks:
		i = i + 1
		current_task.update_state(state='PROGRESS', meta={'process_percent': 90+i})
		if(int(check) == 1):
			a = [cdist(samples, kmeans.cluster_centers_, 'euclidean')]
			b = [np.min(k, axis=1) for k in a]
			wss = [sum(d**2) for d in b]
			wcss = round(wss[0],2)
			text += "WCSS: " + str(wcss) + "\n"
		if(int(check) == 2):
			a = [cdist(samples, kmeans.cluster_centers_, 'euclidean')]
			b = [np.min(k, axis=1) for k in a]
			wcss = [sum(d**2) for d in b]
			tss = sum(pdist(samples,metric='euclidean')**2)/samples.shape[0]
			bss = tss - wcss
			bcss = round(bss[0],2)
			text += "BCSS: " + str(bcss) + "\n"
		if(int(check) == 3):
			calinski = round(calinski_harabaz_score(samples,kmeans.labels_),2)
			text += "Calinski-Harabaz index: " + str(calinski) + "\n"
		if(int(check) == 4):
			davies = round(davies_bouldin_score(samples,kmeans.labels_),2)
			text += "Davis-Bouldin index: " + str(davies) + "\n"
		if(int(check) == 5):
			silhouette = round(silhouette_score(samples,kmeans.labels_),2)
			text += "Silhouette score: " + str(silhouette) + "\n"

	result_path = settings.MEDIA_ROOT + '/result_checks_' + name + '.txt'
	open(result_path,'w').write(text)
				
	result_path = settings.MEDIA_ROOT + '/result_labels_' + name + '.txt'
	np.savetxt(result_path, kmeans.labels_.astype(int), fmt="%i")	

	result_path = settings.MEDIA_ROOT + '/result_centers_' + name + '.txt'
	np.savetxt(result_path, kmeans.cluster_centers_.astype(float))

	current_task.update_state(state='PROGRESS', meta={'process_percent': 100})
