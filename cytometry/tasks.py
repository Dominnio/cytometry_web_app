from __future__ import absolute_import, unicode_literals
from celery import shared_task,current_task
from celery import Celery
from numpy import random
from scipy.fftpack import fft
import time

app = Celery('tasks', backend='amqp', broker='amqp://guest@localhost//')

@shared_task
def fft_random(n):
	"""
	Brainless number crunching just to have a substantial task:
	"""
	for i in range(n):
		x = random.normal(0, 0.1, 2000)
		y = fft(x)
		if(i%30 == 0):
			process_percent = int(100 * float(i) / float(n))
			current_task.update_state(state='PROGRESS', meta={'process_percent': process_percent})
	return random.random()

@shared_task
def add(x,y):
	for i in range(1000000000):
		a = x+y
	return x+y


@shared_task
def add(x, y):
    return x + y


@shared_task
def mul(x, y):
    return x * y


@shared_task
def xsum(numbers):
    return sum(numbers)
