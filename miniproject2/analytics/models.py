from django.db import models
from users.models import User
from courses.models import Course

class ApiRequestLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    endpoint = models.CharField(max_length=255)
    request_time = models.DateTimeField(auto_now_add=True)
    method = models.CharField(max_length=10)

    class Meta:
        db_table = 'api_request_log'
        app_label = 'analytics'
        # Optionally, you could also specify a database to use directly here, though the router should handle it
        # using = 'analytics'

    def __str__(self):
        return f"Request by {self.user.username} to {self.endpoint}"

class CoursePopularity(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    views = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'course_popularity'
        app_label = 'analytics'

    def __str__(self):
        return f"{self.course.name} with {self.views} views"

class UserActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    last_active = models.DateTimeField(auto_now=True)
    total_requests = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'user_activity'
        app_label = 'analytics'

    def __str__(self):
        return f"Activity for {self.user.username}: {self.total_requests} requests"
