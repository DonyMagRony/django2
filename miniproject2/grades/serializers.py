from grades.models import Grade
from rest_framework import serializers


class GradeSerializer(serializers.ModelSerializer):
    teacher = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = Grade
        fields = ['id', 'student', 'course', 'grade', 'teacher', 'date']

