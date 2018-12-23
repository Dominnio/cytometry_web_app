'''

Autor:    		Dominik Orliński 
Prawa autorskie:  	(c) Dominik Orliński 
Data:    		1.01.2019 
Wersja:   		1.0

Ten plik definiuje modele, czyli źródło wiedzy o danych. Modele zawarte w tym pliku 
odpowiadają encjom w bazie danych. Dzięki modelom możemy odwoływać się do obiektów 
w bazie danych z poziomu kodu Pythona.

'''

import datetime
import os
from django 		import forms
from django.conf 	import settings
from django.db 		import models
from django.utils 	import timezone

class Document(models.Model):
    docfile = models.FileField(upload_to='')
    def __unicode__(self):
        return '%s' % (self.docfile.name)
    def delete(self, *args, **kwargs):
        os.remove(os.path.join(settings.MEDIA_ROOT, self.docfile.name))
        super(Document,self).delete(*args,**kwargs)
