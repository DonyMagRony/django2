from grades.models import Grade
from students import serializers


class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = ['id', 'student', 'course', 'grade', 'teacher', 'date']
