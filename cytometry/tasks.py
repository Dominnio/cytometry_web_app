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
	choose = f
	silhouette_best = 0
	for i in range(f,t):
		kmenas = KMeans(i,n_init=n_init,max_iter=max_iter,tol=tol).fit(samples)
		print("gotowe dla: " + str(i) + " plik:" + _file_path)
		silhouette = silhouette_score(samples,kmenas.labels_,metric='euclidean')
		if(silhouette > silhouette_best):
			choose = i
	return choose

@shared_task
def kmeans(file_path, n_clusters, n_init, max_iter, tol, from_val, to_val, checks, name): 
	fcs_data = FlowCal.io.FCSData(file_path)
	samples = np.array(fcs_data, float)
	if(n_clusters == 0):
		n_clusters = determine_number_of_clusters(samples, from_val, to_val, n_init, max_iter, tol, file_path)
	kmeans = KMeans(n_clusters=n_clusters, n_init=n_init, max_iter=max_iter, tol=tol).fit(samples)
	
	current_task.update_state(state='PROGRESS', meta={'process_percent': 100})

	result_path = settings.MEDIA_ROOT + '/result_labels_' + name + '.txt'
	np.savetxt(result_path, kmeans.labels_.astype(int), fmt="%i")	

	result_path = settings.MEDIA_ROOT + '/result_centers_' + name + '.txt'
	np.savetxt(result_path, kmeans.cluster_centers_.astype(float))
