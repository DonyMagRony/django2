# analytics/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('active_users/', views.active_users, name='active_users'),
    path('popular_courses/', views.popular_courses, name='popular_courses'),
]
