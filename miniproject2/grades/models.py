from django.db import models
from students.models import Student
from courses.models import Course
from django.core.validators import MinValueValidator, MaxValueValidator

class Grade(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    grade = models.FloatField(
        validators=[
            MinValueValidator(0.0),  # Minimum value is 0
            MaxValueValidator(100.0)  # Maximum value is 100
        ]
    )
    date = models.DateField(auto_now=True)

    def __str__(self):
        return f"{self.student.user.username} - {self.course.name} - {self.grade}"
