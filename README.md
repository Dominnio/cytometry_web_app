Cytometry Web App is a tool for analyzing cytometric data. It allows you to analyze groups of cells in a sample (provided as a fcs file).

![image](https://raw.githubusercontent.com/Dominnio/cytometry_web_app/master/images/example_1.png)

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
You downloaded the repository, launched the queue manager (RabbitMQ) and started the task queue (Celery).
Now you have to run the Django server. For this purposen in the second terminal, run these commands:
```
  python3 manage.py makemigrations
  python3 manage.py migrate
  python3 manage.py runserver
```

Now open [http://127.0.0.1:8000/cytometry/form_step_0/](http://127.0.0.1:8000/cytometry/form_step_0/) and start use app.

If you want, you can make site accessible in your LAN. In this case, start the server with the command:
```
  python3 manage.py runserver 0.0.0.0:8000
```
Then you can open the page from any device in the same network by entering http://YOUR_IP_ADDRESS:8000/cytometry/form_step_0/
