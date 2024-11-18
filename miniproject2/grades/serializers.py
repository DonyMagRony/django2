from grades.models import Grade
from rest_framework import serializers

class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = ['id', 'student', 'course', 'grade', 'date']
