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
from celery import shared_task,current_task
from celery import task

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

def kmeans(_file_path, _n_clusters, _n_init, _max_iter, _tol, from_val, to_val, checks): 
	n_clusters = _n_clusters
	n_init = _n_init
	max_iter = _max_iter
	tol = _tol
	_f = from_val
	_t = to_val

	fcs_data = FlowCal.io.FCSData(_file_path)
	samples = np.array(fcs_data, float)
	if(_n_clusters == 0):
		_n_clusters = determine_number_of_clusters(samples,_f,_t, _n_init, _max_iter, _tol, _file_path)
	kmeans = KMeans(n_clusters=_n_clusters,n_init=n_init,max_iter=max_iter,tol=tol).fit(samples)
	
	result_path = settings.MEDIA_ROOT + "/documents/result_labels.txt"
	np.savetxt(result_path, kmeans.labels_.astype(int), fmt="%i")	

	result_path = settings.MEDIA_ROOT + "/documents/result_centers.txt"
	np.savetxt(result_path, kmeans.cluster_centers_.astype(float))	

def validate(checks,path_file):
	fcs_data = FlowCal.io.FCSData(path_file)
	channels = fcs_data.channels
	samples = np.array(fcs_data, float)

	result_path = settings.MEDIA_ROOT + "/documents/result_labels.txt"
	theFile = open(result_path, "r")
	labels = []
	for val in theFile.read().split():
	    labels.append(int(val))
	theFile.close()

	result_path = settings.MEDIA_ROOT + "/documents/result_centers.txt"
	cluster_centers_ = np.loadtxt(result_path)

	f = open(settings.MEDIA_ROOT + '/../cytometry/templates/cytometry/evaluation.html','w')
	for i in range(len(checks)):
		if(checks[i] == '1'):
			a = [cdist(samples, cluster_centers_, 'euclidean')]
			b = [np.min(k, axis=1) for k in a]
			wss = [sum(d**2) for d in b]
			wcss = wss[0]
			f.write("<p>WCSS score is = " + str(wcss) + "</p>")	
		if(checks[i] == '2'):
			a = [cdist(samples, cluster_centers_, 'euclidean')]
			b = [np.min(k, axis=1) for k in a]
			wcss = [sum(d**2) for d in b]
			tss = sum(pdist(samples,metric='euclidean')**2)/samples.shape[0]
			bss = tss - wcss
			bcss = bss[0]
			f.write("<p>BCSS score is = " + str(bcss) + "</p>")	
		if(checks[i] == '3'):
			calinski_harabaz = calinski_harabaz_score(samples,labels)
			f.write("<p>Calinski-Harabasz score is = " + str(calinski_harabaz) + "</p>")	
		if(checks[i] == '4'):
			davies_bouldin = davies_bouldin_score(samples,labels)
			f.write("<p>Davies-Bouldin score is = " + str(davies_bouldin) + "</p>")	
		if(checks[i] == '5'):
			silhouette = silhouette_score(samples,labels)
			f.write("<p>Silhouette score is = " + str(silhouette) + "</p>")	
	f.close()

def image_create(dim, pca, dim_1, dim_2, dim_3,path_file):
	fig = plt.figure()

	fcs_data = FlowCal.io.FCSData(path_file)
	channels = fcs_data.channels
	samples = np.array(fcs_data, float)

	result_path = settings.MEDIA_ROOT + "/documents/result_labels.txt"
	theFile = open(result_path, "r")
	labels = []
	for val in theFile.read().split():
	    labels.append(int(val))
	theFile.close()

	if(int(dim) == 1):
		if(pca == True):
			pca = PCA(n_components=1)
			result = pca.fit_transform(samples)
			plt.hist(result[:, 0])
			plt.xlabel("PCA - 1")
		else:
			plt.hist(samples[:, int(dim_1)])
			plt.xlabel(str(channels[int(dim_1)]))

	if(int(dim) == 2):
		print(pca)
		if(pca == True):
			pca = PCA(n_components=2)
			result = pca.fit_transform(samples)
			plt.scatter(result[:, 0], result[:, 1], c=labels, s=5, cmap='viridis')
			plt.xlabel("PCA - 1")
			plt.ylabel("PCA - 2")
		else:
			plt.scatter(samples[:, int(dim_1)], samples[:, int(dim_2)], c=labels, s=5, cmap='viridis')
			plt.xlabel(str(channels[int(dim_1)]))
			plt.ylabel(str(channels[int(dim_2)]))

	if(int(dim) == 3):
		if(pca == True):
			pca = PCA(n_components=3)
			result = pca.fit_transform(samples)
			ax = fig.add_subplot(111, projection='3d')
			ax.scatter(result[:, 0], result[:, 1], result[:, 2], c=labels, s=1, cmap='viridis')
			ax.set_xlabel('PCA - 1')
			ax.set_ylabel('PCA - 2')
			ax.set_zlabel('PCA - 3')
		else:
			ax = fig.add_subplot(111, projection='3d')
			ax.scatter(samples[:, int(dim_1)], samples[:, int(dim_2)], samples[:, int(dim_3)], c=labels, s=1, cmap='viridis')
			ax.set_xlabel(str(channels[int(dim_1)]))
			ax.set_ylabel(str(channels[int(dim_2)]))
			ax.set_zlabel(str(channels[int(dim_3)]))

	plt.title('KMeans')
	plt.grid(True)
	plt.savefig(settings.MEDIA_ROOT + '/../cytometry/static/cytometry/images/real_data_result.png')

