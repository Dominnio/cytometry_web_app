'''

Autor:    		Dominik Orliński 
Prawa autorskie:  	(c) Dominik Orliński 
Data:    		1.01.2019 
Wersja:   		1.0

'''

from django 		import forms
from django.conf 	import settings
import numpy as np
import FlowCal

def get_my_choices(path_file):
    fcs_data = FlowCal.io.FCSData(path_file)
    channels = fcs_data.channels
    choices = []
    for i in range(len(channels)):
        choices.append((i,channels[i]))
    return choices

class MyForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(MyForm, self).__init__(*args, **kwargs)
        self.fields['my_choice_field'] = forms.ChoiceField(choices=get_my_choices(args[0])
    )

def get_shape(name):
    path_to_samples = settings.MEDIA_ROOT + "/" + name
    fcs_data = FlowCal.io.FCSData(path_to_samples)
    shape = fcs_data.shape
    return shape

def get_channels(name):
    path_to_samples = settings.MEDIA_ROOT + "/" + name
    fcs_data = FlowCal.io.FCSData(path_to_samples)
    channels = fcs_data.channels
    return channels

def get_samples(name):
    path_to_samples = settings.MEDIA_ROOT + "/" + name
    fcs_data = FlowCal.io.FCSData(path_to_samples)
    samples = np.array(fcs_data, float)
    return samples

class SamplesForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.samples = get_samples(args[0])
        self.channels = get_channels(args[0])
        self.shape = get_shape(args[0])

class DocumentForm(forms.Form):
    docfile = forms.FileField(
        label='Select & upload a file',
        help_text='file should be in the fcs format & have max. 10 megabytes'
    )

def get_number_of_cluster(name):
    path_to_centers = settings.MEDIA_ROOT + "/result_centers_" + name + ".txt"
    with open(path_to_centers) as textFile:
        lines = [line.split() for line in textFile]    
    return len(lines)


class Cluster():
    def __init__(self, number_of_cells, center):
        self.number_of_cells = number_of_cells
        self.center = center

def get_clusters(name):
    clusters = []
    path_to_centers = settings.MEDIA_ROOT + "/result_centers_" + name + ".txt"
    with open(path_to_centers) as textFile:
        lines = [line.split() for line in textFile]
    for line in lines:
        for dim in line:
            dim = round(float(dim),2)            
    sizes = np.zeros(len(lines), dtype=int)
    path_to_labels = settings.MEDIA_ROOT + "/result_labels_" + name + ".txt"
    textFile = open(path_to_labels,'r')
    for line in textFile:
        sizes[int(line)] += 1
    for i in range(len(lines)):
        dims = []
        for dim in lines[i]:
            dim = round(float(dim),2)
            dims.append(dim)
        cluster = Cluster(sizes[i],dims)
        clusters.append(cluster)     
    return clusters

def get_checks(name):
    path_to_checks = settings.MEDIA_ROOT + "/result_checks_" + name + ".txt"
    with open(path_to_checks) as textFile:
        lines = textFile.readlines()
    return lines

class ResultForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.n_clusters = get_number_of_cluster(args[0])
        self.clusters = get_clusters(args[0])
        self.checks = get_checks(args[0])
