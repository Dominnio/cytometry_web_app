import datetime
from django import forms
import os
from django.conf import settings
from django.db import models
from django.utils import timezone

class Document(models.Model):
    docfile = models.FileField(upload_to='documents')
    def __unicode__(self):
        return '%s' % (self.docfile.name)
    def delete(self, *args, **kwargs):
        os.remove(os.path.join(settings.MEDIA_ROOT, self.docfile.name))
        super(Document,self).delete(*args,**kwargs)

# Create your models here.
