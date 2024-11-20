from django.contrib import admin
from .models import ApiRequestLog,UserActivity,CoursePopularity

# Register your models here.
admin.site.register(ApiRequestLog)
admin.site.register(UserActivity)
admin.site.register(CoursePopularity)