from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from attendance.models import Attendance
from attendance.serializers import AttendanceSerializer

from users.permissions import IsAdmin, IsTeacher
# Create your views here.
class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]
    def get_permissions(self):
        if self.action in ['create', 'update', 'destroy']:
            return [ IsTeacher()]  
        return [IsAdmin()] 
