# Auction ✈️


![Django DRF Logo](logos/django-rest.jpg)
![Redis Logo](logos/redis-image.svg)
![Celery Logo](logos/celery.png)
![Prometheus Logo](logos/prometheus.png)
![Grafana Logo](logos/grafana.png)

> Django REST project 

This is a Django REST Framework (DRF) powered API for managing air services, such as airports, flights, tickets and related entities. The API is designed to handle essential functionalities for an air transport system, including flight scheduling, airport management, and user interactions. 


## Run service on your machine

1. Clone repository  
```shell
git clone https://github.com/dimak20/airport-service.git
cd airport-service
```
2. Then, create and activate .venv environment  
```shell
python -m venv env
```
For Unix system
```shell
source venv/bin/activate
```

For Windows system

```shell
venv\Scripts\activate
```

3. Install requirements.txt by the command below  


```shell
pip install -r requirements.txt
```

4. You need to make migrations
```shell
python manage.py makemigrations
python manage.py migrate
```
5. (Optional) Also you can load fixture data
```shell
python manage.py loaddata data.json
```
email: admin_test@gmail.com

password: test_password

6. And finally, create superuser and run server

```shell
python manage.py createsuperuser
python manage.py runserver # http://127.0.0.1:8000/
```

## Run with Docker (simple version)

1. Clone repository  
```shell
git clone https://github.com/dimak20/airport-service.git
cd airport-service
```
2. Create .env file and set up environment variables
```shell
DATABASE_ENGINE=postgresql
POSTGRES_PASSWORD=airport
POSTGRES_USER=airport
POSTGRES_DB=airport
POSTGRES_HOST=db
POSTGRES_PORT=5432
PGDATA=/var/lib/postgresql/data/pgdata
DJANGO_SECRET_KEY=your_secret_key
DJANGO_DEBUG=true
DATABASE_URL=postgresql://airport:airport@db:5432/airport
USE_REDIS=fale
```

3. Build and run docker containers 


```shell
docker-compose -f docker-compose.yaml up --build
```

4. (Optionally) Create super user inside docker container and load data

```shell
docker exec -it <your_container_name> sh
python manage.py createsuperuser
python manage.py loaddata data.json
```
email: admin_test@gmail.com

password: test_password

You can find out container name by the command "docker ps" -> your air_service id

5. Access the API at http://localhost:8000/api/v1/

## Run with Docker (advanced monitoring version)

1. Clone repository  
```shell
git clone https://github.com/dimak20/airport-service.git
cd airport-service
```
2. Create .env file and set up environment variables
```shell
DATABASE_ENGINE=postgresql
POSTGRES_PASSWORD=airport
POSTGRES_USER=airport
POSTGRES_DB=airport
POSTGRES_HOST=db
POSTGRES_PORT=5432
PGDATA=/var/lib/postgresql/data/pgdata
DJANGO_SECRET_KEY=your_secret_key
DJANGO_DEBUG=true
REDIS_URL=redis://redis:6379/0
GF_SECURITY_ADMIN_USER=admin
GF_SECURITY_ADMIN_PASSWORD=admin
REDIS_HOST=redis
REDIS_PORT=6379
DATABASE_URL=postgresql://airport:airport@db:5432/airport
CELERY_BROKER_URL=redis://redis:6379/0
USE_REDIS=true
DEFAULT_FROM_EMAIL=example@mail.com
SENDGRID_API_KEY=your_secret_key
```

3. Build and run docker containers 


```shell
docker-compose -f docker-compose.monitoring.yml up --build
```

4. (Optionally) Create super user inside docker container and load data

```shell
docker exec -it <your_container_name> sh
python manage.py createsuperuser
python manage.py loaddata data.json
```
email: admin_test@gmail.com

password: test_password

You can find out container name by the command "docker ps" -> your air_service id


5. Access the API at http://localhost:8000/api/v1/


6. Monitoring
```shell
Prometheus: http://localhost:9090
Grafana: http://localhost:3000
Beat scheduler: http://localhost:8000/admin/ -> tasks
```

### Project configuration

Your project needs to have this structure


```plaintext
Project
├── air_service
|   └── management
|   |  └── commands
|   |     └── wait_for_db.py
│   ├── __init__.py
│   └── admin.py
│   ├── apps.py
|   ├── filters.py
|   ├── models.py
│   ├── ordering.py
|   ├── permissions.py
|   ├── serializers.py
|   ├── signals.py
|   ├── tasks.py
│   ├── urls.py
│   └── views.py
|
|
├── airport_api_service
│   ├── __init__.py
│   ├── asgi.py
│   ├── asgi.py
│   ├──celery.py
│   ├── settings.py
│   └── urls.py
│   
├── media
│   
├── logos
│   
├── templates
|
├── user
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├──models.py
│   ├── serializers.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
├── .dockerignore
│
├── .env
│
├── .gitignore
│
├── docker-compose.monitoring.yml
│
├── docker-compose.yaml
│
├── Docker
│
├── manage.py
│
├── prometheus.yml
│
├── README.md
|
└── requirements.txt
```


## Usage
* Flight Endpoints: Manage flights, routes, and schedules.
* Airport Endpoints: Retrieve and manage airport information.
* User Endpoints: User registration, login, and token authentication.
* Hint - use http://localhost:8000/api/v1/doc/swagger/ to see all endpoints

## Features
* JWT Authentication
* Admin panel /admin/
* Swagger documentation
* Managing orders and tickets
* Creating countries, cities, flights, routes, crews, airplanes, airplane types, airports
* Creaing orders and tickets 
* Filtering and ordering all models by name, distance etc.
* Celery usage for background tasks
* Redis usage for caching
* Prometheus usage for service monitoring
* Grafana for visualizing server usage
* Beat for scheduling background tasks
