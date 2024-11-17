from django.db import models
from students.models import Student
from courses.models  import Course

class Grade(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    grade = models.CharField(max_length=5)
    date = models.DateField(auto_now=True)
