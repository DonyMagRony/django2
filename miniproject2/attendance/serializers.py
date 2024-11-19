# attendance/serializers.py
from rest_framework import serializers  # Ensure this is the correct import
from attendance.models import Attendance

class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ['id', 'student', 'course', 'date', 'status']
