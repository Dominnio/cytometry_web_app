from django import forms
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
