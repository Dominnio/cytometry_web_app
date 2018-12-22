'''

Autor:    		Dominik Orliński 
Prawa autorskie:  	(c) Dominik Orliński 
Data:    		1.01.2019 
Wersja:   		1.0

'''

from django.test import TestCase
from django.http import HttpRequest
from django.test import SimpleTestCase
from django.urls import reverse
from django.test import Client

class HomePageTests(SimpleTestCase):

    def test_home_page_status_code(self):
        response = self.client.get('/')
        self.assertEquals(response.status_code, 200)

    def test_run(self):
        c = Client()
        response = self.client.post('/step_2/', 
                                   {'file_name': '../cytometry/documents/test.fcs',
                                    'checks[]': [1,2,3], 
                                    'from': 2, 'to': 7, 
                                    'n_clusters': -1, 
                                    'n_init': 10, 
                                    'max_iter': 300, 
                                    'tol': 0.001})
        self.assertEquals(response.status_code, 302)

# Create your tests here.
