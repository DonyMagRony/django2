from django.urls import path
from .views import UpdateRoleView

urlpatterns = [
    path('users/<int:pk>/role/', UpdateRoleView.as_view(), name='update-role'),
]
