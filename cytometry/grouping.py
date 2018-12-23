'''

Autor:    		Dominik Orliński 
Prawa autorskie:  	(c) Dominik Orliński 
Data:    		1.01.2019 
Wersja:   		1.0

Plik pomocniczy.

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
from sklearn.cluster 		import KMeans
from sklearn 			import preprocessing as pre
from sklearn.decomposition 	import PCA
from sklearn.metrics 		import calinski_harabaz_score
from sklearn.metrics 		import davies_bouldin_score
from sklearn.metrics 		import silhouette_score
from scipy.spatial.distance 	import cdist, pdist
from django.conf 		import settings

def image_create(dim, pca, dim_1, dim_2, dim_3, path_file, name, preprocessing):
    fig = plt.figure()

    fcs_data = FlowCal.io.FCSData(path_file)
    channels = fcs_data.channels
    samples = np.array(fcs_data, float)
    print(preprocessing)
    if(preprocessing):
        samples = pre.scale(samples, axis=0)

    result_path = settings.MEDIA_ROOT + "/result_labels_" + name + ".txt"
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
        if(pca == True):
            pca = PCA(n_components=2)
            result = pca.fit_transform(samples)
            plt.scatter(result[:, 0], result[:, 1], c=labels, s=0.2, cmap='viridis')
            plt.xlabel("PCA - 1")
            plt.ylabel("PCA - 2")
        else:
            plt.scatter(samples[:, int(dim_1)], samples[:, int(dim_2)], c=labels, s=0.2, cmap='viridis')
            plt.xlabel(str(channels[int(dim_1)]))
            plt.ylabel(str(channels[int(dim_2)]))

    if(int(dim) == 3):
        if(pca == True):
            pca = PCA(n_components=3)
            result = pca.fit_transform(samples)
            ax = fig.add_subplot(111, projection='3d')
            ax.scatter(result[:, 0], result[:, 1], result[:, 2], c=labels, s=0.2, cmap='viridis')
            ax.set_xlabel('PCA - 1')
            ax.set_ylabel('PCA - 2')
            ax.set_zlabel('PCA - 3')
        else:
            ax = fig.add_subplot(111, projection='3d')
            ax.scatter(samples[:, int(dim_1)], samples[:, int(dim_2)], samples[:, int(dim_3)], c=labels, s=0.2, cmap='viridis')
            ax.set_xlabel(str(channels[int(dim_1)]))
            ax.set_ylabel(str(channels[int(dim_2)]))
            ax.set_zlabel(str(channels[int(dim_3)]))

    plt.title('KMeans')
    plt.grid(True)
    plt.savefig(settings.STATIC_ROOT + '/cytometry/static/real_data_result_' + name + '.png')
    return 1

