from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView,TokenBlacklistView

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
    path('token/',TokenObtainPairView.as_view(),name='token_obtain_pair'),
    path('token/refresh/',TokenRefreshView.as_view(),name='token_refresh'),
    path('token/blacklist/',TokenBlacklistView.as_view(),name='token_blacklist'),

    path('users/', include('users.urls')),
    path('students/', include('students.urls')),
    path('courses/', include('courses.urls')),
    path('grades/', include('grades.urls')),
    path('attendance/', include('attendance.urls')),
    path('analytics/', include('analytics.urls')),

    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('', lambda request: redirect('users/register')),
]


from django.conf import settings

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [  # Append the debug toolbar URLs
        path('__debug__/', include(debug_toolbar.urls)),
    ]