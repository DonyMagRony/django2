from django.core.cache import cache  # Correct import for caching
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Student
from .serializers import StudentSerializer

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        student_id = kwargs.get("pk")
        cache_key = f"student_{student_id}"
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data, status=status.HTTP_200_OK)

        # Fetch from DB and cache it
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        cache.set(cache_key, serializer.data, timeout=3600)  # Cache for 1 hour
        return Response(serializer.data)

    def perform_update(self, serializer):
        instance = serializer.save()
        cache.delete(f"student_{instance.id}")

    def get_queryset(self):
        if self.request.user.role == 'student':
            return self.queryset.filter(user=self.request.user)
        return self.queryset
