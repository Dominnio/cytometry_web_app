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
from numpy import random
from sklearn.cluster import KMeans
from sklearn import preprocessing as pre
from sklearn.decomposition import PCA
from sklearn.metrics import calinski_harabaz_score
from sklearn.metrics import davies_bouldin_score
from sklearn.metrics import silhouette_score
from scipy.spatial.distance import cdist, pdist
from django.conf import settings
from celery import shared_task,current_task,task

def determine_number_of_clusters(name, samples, min_clusters, max_clusters, n_init, max_iter, tol, preprocessing):
    k = 0
    calinski_best = 0
    calinski_results = []

    davies_best = 0
    davies_results = []

    sil_best = 0
    sil_results = []

    for i in range(min_clusters, max_clusters):
        progress = 80 * float(i - min_clusters) / float(max_clusters - min_clusters)
        if(preprocessing):
            samples = pre.scale(samples, axis=0)
        kmenas = KMeans(i,n_init=n_init,max_iter=max_iter,tol=tol).fit(samples)

        calinski = calinski_harabaz_score(samples,kmenas.labels_)
        calinski_results.append(calinski)

        davies = davies_bouldin_score(samples,kmenas.labels_)
        davies_results.append(davies)

        #sil = silhouette_score(samples,kmenas.labels_)
        #sil_results.append(sil)

        #wss = kmenas.inertia_
        #tss = sum(pdist(samples)**2)/samples.shape[0]
        #bss = tss - wss
        #print(bss/wss * (samples.shape[0] - i) / (i - 1)) # im wiekszy ten stosunek tym lepiej

        current_task.update_state(state='PROGRESS', meta={'process_percent': progress})
        if(calinski > calinski_best):
            k = i
            calinski_best = calinski


    fig, ax1 = plt.subplots()
    t = np.arange(min_clusters, max_clusters)
    s1 = calinski_results
    ax1.plot(t, s1, 'b-')
    ax1.set_xlabel('number of clusters')
    # Make the y-axis label, ticks and tick labels match the line color.
    ax1.set_ylabel('Calinski-Harabasz', color='b')
    ax1.tick_params('y', colors='b')

    ax2 = ax1.twinx()
    s2 = davies_results
    ax2.plot(t, s2, 'r-')
    ax2.set_ylabel('Davies-Bouldin', color='r')
    ax2.tick_params('y', colors='r')

    #ax3 = ax1.twinx()
    #s3 = sil_results
    #ax3.plot(t, s3, 'g-')
    #ax3.set_ylabel('Silhouette score', color='g')
    #ax3.tick_params('y', colors='g')
    #ax3.tick_params(axis='y', pad=100)

    fig.tight_layout()
    plt.savefig(settings.STATIC_ROOT + '/cytometry/static/calinski_results_' + name + '.png')
        
    return k

@task(bind=True)
def kmeans(self, file_path, n_clusters, n_init, max_iter, tol, from_val, to_val, checks, name, preprocessing): 
    current_task.update_state(state='PROGRESS', meta={'process_percent': 0})

    fcs_data = FlowCal.io.FCSData(file_path)
    samples = np.array(fcs_data, float)
    if(n_clusters == 0):
        n_clusters = determine_number_of_clusters(name, samples, from_val, to_val, n_init, max_iter, tol, preprocessing)
    if(preprocessing):
        samples = pre.scale(samples, axis=0)
    kmeans = KMeans(n_clusters=n_clusters, n_init=n_init, max_iter=max_iter, tol=tol).fit(samples)
    current_task.update_state(state='PROGRESS', meta={'process_percent': 75})
    i = 0
    text = ""
    for check in checks:
        i = i + 5
        current_task.update_state(state='PROGRESS', meta={'process_percent': 75+i})
        if(int(check) == 1):
            wss = kmeans.inertia_
            wcss = round(wss,2)
            text += "WCSS: " + str(wcss) + "\n"
        if(int(check) == 2):
            wcss = kmeans.inertia_
            tss = sum(pdist(samples,metric='euclidean')**2)/samples.shape[0]
            bss = tss - wcss
            bcss = round(bss,2)
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
