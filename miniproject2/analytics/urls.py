from django.urls import path
from . import views

urlpatterns = [
    path('api-usage/', views.api_usage_graph, name='api_usage_graph'),
    path('most-active-users/', views.most_active_users, name='most_active_users'),
]
