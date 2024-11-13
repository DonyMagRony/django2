from django.db import models
from django.contrib.auth.models import AbstractUser 
# Create your models here.
ROLE_CHOICE = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('admin', 'Admin')  
    ]
class User(AbstractUser):
    role = models.CharField(max_length=10,choices=ROLE_CHOICE)
