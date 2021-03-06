'''

Autor:    		Dominik Orliński 
Prawa autorskie:  	(c) Dominik Orliński 
Data:    		1.01.2019 
Wersja:   		1.0

W tym pliku zdefiowane są zadania dla kolejki zadań Celery.

'''

import imp
import FlowCal
import gi
import time
import os
import time
import pandas as pd
import numpy as np
import glob
import matplotlib.pyplot as plt
gi.require_version('Gtk', '3.0')

from gi.repository 		import Gtk
from numpy 			import random
from sklearn.cluster 		import KMeans
from sklearn 			import preprocessing as pre
from sklearn.decomposition 	import PCA
from sklearn.metrics 		import calinski_harabaz_score
from sklearn.metrics 		import davies_bouldin_score
from sklearn.metrics 		import silhouette_score
from scipy.spatial.distance 	import cdist, pdist
from django.conf 		import settings
from celery 			import shared_task,current_task,task
from scipy.spatial 		import distance

import ctypes
import numpy.ctypeslib as ctl
from numpy.ctypeslib 		import ndpointer

# impor bliblioteki dzielonej z C++
lib = ctypes.cdll.LoadLibrary(settings.BASE_DIR + "/cytometry/cpp_module/my_kmeans.so")
my_kmeans = lib.kmeans
my_kmeans.restype = None
my_kmeans.argtypes = [ctl.ndpointer(dtype=np.uint64),
                      ctl.ndpointer(dtype=np.uint64),
                      ctl.ndpointer(np.int32),
                      ctl.ndpointer(np.double),
                      ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_double, ctypes.c_int, ctypes.c_int]

def determine_number_of_clusters(name, samples, min_clusters, max_clusters, n_init, max_iter, tol, preprocessing):
    k = 0
    calinski_best = 0
    calinski_results = []

    davies_best = 0
    davies_results = []

    for i in range(min_clusters, max_clusters):
        progress = 80 * float(i - min_clusters) / float(max_clusters - min_clusters)
        if(preprocessing):
            samples = pre.scale(samples, axis=0)

        samplespp = (samples.__array_interface__['data'][0] + np.arange(samples.shape[0])*samples.strides[0]).astype(np.uintp)
        my_centers = np.ndarray(shape=(i,samples.shape[1]),dtype=np.double)
        my_centerspp = (my_centers.__array_interface__['data'][0] + np.arange(my_centers.shape[0])*my_centers.strides[0]).astype(np.uintp)
        my_labels = np.zeros(samples.shape[0],dtype=np.int32)
        my_stats = np.zeros(4,dtype=np.double)

        my_kmeans(samplespp, my_centerspp, my_labels, my_stats, samples.shape[0], i, samples.shape[1], tol, n_init, max_iter)

        calinski = calinski_harabaz_score(samples,my_labels)
        calinski_results.append(calinski)

        davies = davies_bouldin_score(samples,my_labels)
        davies_results.append(davies)

        current_task.update_state(state='PROGRESS', meta={'process_percent': progress})
        if(calinski > calinski_best):
            k = i
            calinski_best = calinski

    # stworzenie wykresów miara(k)
    fig, ax1 = plt.subplots()
    t = np.arange(min_clusters, max_clusters)
    s1 = calinski_results
    ax1.plot(t, s1, 'b-')
    ax1.set_xlabel('number of clusters')
    ax1.set_ylabel('Calinski-Harabasz', color='b')
    ax1.tick_params('y', colors='b')

    ax2 = ax1.twinx()
    s2 = davies_results
    ax2.plot(t, s2, 'r-')
    ax2.set_ylabel('Davies-Bouldin', color='r')
    ax2.tick_params('y', colors='r')

    fig.tight_layout()
    plt.savefig(settings.STATIC_ROOT + '/cytometry/static/calinski_results_' + name + '.png')
  
    return k

# algorytm k-średnich i weryfikacja rozwizania
@task(bind=True)
def kmeans(self, file_path, n_clusters, n_init, max_iter, tol, from_val, to_val, checks, name, preprocessing): 
    current_task.update_state(state='PROGRESS', meta={'process_percent': 0})

    if(os.path.isfile(settings.STATIC_ROOT + '/cytometry/static/calinski_results_' + name + '.png')):
        os.remove(settings.STATIC_ROOT + '/cytometry/static/calinski_results_' + name + '.png')

    fcs_data = FlowCal.io.FCSData(file_path)
    samples = np.array(fcs_data, float)
    if(n_clusters == 0):
        n_clusters = determine_number_of_clusters(name, samples, from_val, to_val, n_init, max_iter, tol, preprocessing)
    if(preprocessing):
        samples = pre.scale(samples, axis=0)

    samplespp = (samples.__array_interface__['data'][0] + np.arange(samples.shape[0])*samples.strides[0]).astype(np.uintp)
    my_centers = np.ndarray(shape=(n_clusters,samples.shape[1]),dtype=np.double)
    my_centerspp = (my_centers.__array_interface__['data'][0] + np.arange(my_centers.shape[0])*my_centers.strides[0]).astype(np.uintp)
    my_labels = np.zeros(samples.shape[0],dtype=np.int32)
    my_stats = np.zeros(4,dtype=np.double)

    my_kmeans(samplespp, my_centerspp, my_labels, my_stats, samples.shape[0], n_clusters, samples.shape[1], tol, n_init, max_iter)

    current_task.update_state(state='PROGRESS', meta={'process_percent': 75})
    i = 0
    text = ""
    for check in checks:
        i = i + 5
        current_task.update_state(state='PROGRESS', meta={'process_percent': 75+i})
        if(int(check) == 1):
            wss = my_stats[3]
            wcss = round(wss,2)
            text += "WCSS: " + str(wcss) + "\n"
        if(int(check) == 2):
            wcss = my_stats[3]
            total_center = [samples.mean(axis=0)]
            arr = cdist(samples, total_center, 'euclidean')
            tss = 0 
            for a in arr:
                tss += a**2
            bss = tss - wcss
            bcss = round(bss[0],2)
            text += "BCSS / WCSS: " + str(bcss/wcss) + "\n"
        if(int(check) == 3):
            calinski = round(calinski_harabaz_score(samples,my_labels),2)
            text += "Calinski-Harabaz index: " + str(calinski) + "\n"
        if(int(check) == 4):
            davies = round(davies_bouldin_score(samples,my_labels),2)
            text += "Davis-Bouldin index: " + str(davies) + "\n"
        if(int(check) == 5):
            silhouette = round(silhouette_score(samples,my_labels),2)
            text += "Silhouette score: " + str(silhouette) + "\n"

    result_path = settings.MEDIA_ROOT + '/result_checks_' + name + '.txt'
    open(result_path,'w').write(text)
    result_path = settings.MEDIA_ROOT + '/result_labels_' + name + '.txt'
    np.savetxt(result_path, my_labels.astype(int), fmt="%i")
    result_path = settings.MEDIA_ROOT + '/result_centers_' + name + '.txt'
    np.savetxt(result_path, my_centers.astype(float))

    result_path = settings.MEDIA_ROOT + '/pretty_result_' + name + '.txt'
    pretty_result = open(result_path,'w')
    pretty_result.write("Number of cluster: " + str(n_clusters))
    pretty_result.write("\n\nCenters parameters: \n")
    for i in range(len(my_centers)):
        pretty_result.write(str(my_centers[i]) + "\n")
    pretty_result.write("\n\nLabels: \n")
    in_line = 0
    for i in range(len(my_labels)):
        pretty_result.write(str(my_labels[i]))
        in_line += 1
        if(in_line > 100):
            in_line = 0
            pretty_result.write("\n") 
    pretty_result.close()  

    current_task.update_state(state='PROGRESS', meta={'process_percent': 100})
