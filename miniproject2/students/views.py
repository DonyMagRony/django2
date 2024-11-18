from django.core.cache import cache
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Student
from .serializers import StudentSerializer
from users.permissions import IsStudent  # Import the custom permission

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]  # Ensure user is authenticated

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
        """
        If the user is a student, restrict access to their own data.
        Admins or non-students can access the full list.
        """
        if IsStudent().has_permission(self.request, self):
            return self.queryset.filter(user=self.request.user)
        return self.queryset
