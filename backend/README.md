#### Run Backend
1. Clone the repo
2. Go to ***backend*** directory
3. Create a virtualenv ```virtualenv venv```
4. Activate the virtualenv ```source venv/bin.activate```
5. Install all the library ```pip install -r requirements.txt```
6. Rename ***.env-example*** to ***.env*** located in ```/backend/hackathon_adhaar_solution/```
7. Update **FAST2SMS_API_KEY** & **GOOGLE_MAPS_API_KEY** and other variables in ***.env***
8. Run ```python manage.py makemigrations```
9. Run ```python manage.py migrate```
10. Run ```python manage.py runserver```
11. You can create superuser by ```python manage.py createsuperuser```