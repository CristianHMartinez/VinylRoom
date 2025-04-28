import os
import django
from django.contrib.auth.models import User

# Configura Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djangocrud.settings")
django.setup()

# Crea el superusuario
username = 'Cristian'
email = 'cristian.martinez.716cm9@gmail.com'
password = '#Chris23072003 '

user, created = User.objects.get_or_create(username=username, email=email)
if created:
    user.set_password(password)
    user.is_superuser = True
    user.is_staff = True
    user.save()
    print("Superuser created successfully!")
else:
    print("Superuser already exists.")