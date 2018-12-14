Cytometry Web App is a tool for analyzing cytometric data. It allows you to analyze groups of cells in a sample (provided as a fcs file).
The application is available at the address [cytometry.hopto.org](http://cytometry.hopto.org:8000). It is possible that you have to enable the port 8000 in your firewall.

![image](https://raw.githubusercontent.com/Dominnio/cytometry_web_app/master/images/example_1.png)

# Requirements
* Python: 3.6.7
* Django: 2.1.4
* Celery: 3.1.26
* RabbitMQ: 3.6.10

# Download & run
Clone this repository, go to cytometry_web_app directory, create static directory for images:
```
  git clone https://github.com/Dominnio/cytometry_web_app.git
  cd cytometry_web_app
  mkdir cytometry/static
```

Now you have to launch the queue manager (RabbitMQ) and start the task queue (Celery). In the terminal, run these commands:
```
  sudo rabbitmq-server
  celery -A mysite worker -l info
```
In the terminal will appear the task queue logs. 

Now you have to prepare and run the Django server. For this purpose in the second terminal, run these commands:
```
  python3 manage.py makemigrations
  python3 manage.py migrate
  python3 manage.py runserver
```
Here you will receive information about the requests sent to the server.

Now open [http://127.0.0.1:8000](http://127.0.0.1:8000) and start use app.

If you want, you can make site accessible in your LAN. In this case, start the server with the command:
```
  python3 manage.py runserver 0.0.0.0:8000
```
Then you can open the page from any device in the same network by entering http://YOUR_IP_ADDRESS:8000
