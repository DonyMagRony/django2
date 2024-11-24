from django.contrib import admin
from .models import CourseMetric,APIRequestLog 

@admin.register(APIRequestLog)
class APIMetricAdmin(admin.ModelAdmin):
    list_display = ('user', 'endpoint', 'timestamp')

@admin.register(CourseMetric)
class PopularCourseMetricAdmin(admin.ModelAdmin):
    list_display = ('course', 'views', 'last_accessed')
