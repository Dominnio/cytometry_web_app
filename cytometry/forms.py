from django import forms
from django.conf import settings
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

class DocumentForm(forms.Form):
    docfile = forms.FileField(
        label='Select & upload a file',
        help_text='file should be in the fcs format & have max. 10 megabytes'
    )

def get_general_info_about_result(name):
	path_to_centers = settings.MEDIA_ROOT + "/result_centers_" + name + ".txt"
	with open(path_to_centers) as textFile:
		lines = [line.split() for line in textFile]	
	return len(lines)

def get_sizes_of_clusters(name):
	path_to_centers = settings.MEDIA_ROOT + "/result_centers_" + name + ".txt"
	with open(path_to_centers) as textFile:
		lines = [line.split() for line in textFile]
	sizes = np.zeros(len(lines), dtype=int)
	
	path_to_labels = settings.MEDIA_ROOT + "/result_labels_" + name + ".txt"
	textFile = open(path_to_labels,'r')
	for line in textFile:
		sizes[int(line)] += 1
	return sizes

class ResultForm(forms.Form):
	def __init__(self, *args, **kwargs):
		self.general = get_general_info_about_result(args[0])
		self.sizes = get_sizes_of_clusters(args[0])
