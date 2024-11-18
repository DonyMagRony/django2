from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomUserViewSet, UpdateRoleView

# Define the router and register the custom user viewset
router = DefaultRouter()
router.register('register', CustomUserViewSet, basename='user')

# Define the URL patterns
urlpatterns = [
    path('', include(router.urls)),
    path('<int:pk>/role/', UpdateRoleView.as_view(), name='update-role'),
]

