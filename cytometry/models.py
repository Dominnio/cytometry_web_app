import datetime
import os
from django import forms
from django.conf import settings
from django.db import models
from django.utils import timezone

class Document(models.Model):
    docfile = models.FileField(upload_to='')
    def __unicode__(self):
        return '%s' % (self.docfile.name)
    def delete(self, *args, **kwargs):
        os.remove(os.path.join(settings.MEDIA_ROOT, self.docfile.name))
        super(Document,self).delete(*args,**kwargs)

class Calcu(models.Model):
    n = models.CharField(max_length=10)

# Create your models here.
