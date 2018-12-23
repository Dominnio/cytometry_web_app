'''

Autor:    		Dominik Orliński 
Prawa autorskie:  	(c) Dominik Orliński 
Data:    		1.01.2019 
Wersja:   		1.0

W tym pliku można zarejestrować modele, które będą dostępne z poziomu strony administratora.

'''

from django.contrib 	import admin
from .models 		import Document

admin.site.register(Document)
