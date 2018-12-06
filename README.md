# Requirements
* Python: 3.6.7
* Django: 2.1.4
* Celery: 3.1.26
* RabbitMQ: 3.6.10

# Download & run
In the terminal, run these commands:
```
  git clone https://github.com/Dominnio/cytometry_web_app.git
  cd cytometry_web_app
  sudo rabbitmq-server
  celery -A mysite worker -l info
```
You downloaded the repository, launched the message queue manager (RabbitMQ) and started the task queue (Celery).
Now you have to run the Django server. For this purposen in the second terminal, run these commands
```
  python3 manage.py makemigrations
  python3 manage.py migrate
  python3 manage.py runserver

```

Now open [http://127.0.0.1:8000/cytometry/form/](http://127.0.0.1:8000/cytometry/form/) and start use app.
