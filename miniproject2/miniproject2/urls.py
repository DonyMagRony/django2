from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

# Swagger schema view
schema_view = get_schema_view(
    openapi.Info(
        title="Student Management API",
        default_version='v1',
        description="API documentation for the Student Management System",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="support@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),

    # Include app-specific URLs with clean prefixes
    path('users', include('users.urls')),
    path('students/', include('students.urls')),
    path('courses/', include('courses.urls')),
    path('grades/', include('grades.urls')),
    path('attendance/', include('attendance.urls')),
    # path('analytics/', include('analytics.urls')),
    # Swagger and ReDoc
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
