from django.db import models
from django.contrib.auth.models import User

class APIRequestLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    endpoint = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'analytics'


class CourseMetric(models.Model):
    course_name = models.CharField(max_length=255)
    views = models.IntegerField(default=0)
    last_viewed = models.DateTimeField(auto_now=True)
    class Meta:
        app_label = 'analytics'

