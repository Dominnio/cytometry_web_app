'''

Autor:    		Dominik Orliński 
Prawa autorskie:  	(c) Dominik Orliński 
Data:    		1.01.2019 
Wersja:   		1.0

Główny plik konfiguracyjny URL, zawiera listę ścieżek URL, które przekierowują żądanie 
do odpowiednich aplikacji, które następnie w swoich plikach konfiguracyjnych URL 
przekierowują to żądanie do widoków zdefiniowanych w views.py. 

'''

from django.contrib 	import admin
from django.urls 	import include, path
from django.conf.urls 	import include, url

urlpatterns = [
    path('', include('cytometry.urls')),
    url(r'^admin/', admin.site.urls),
]
