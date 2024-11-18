from django.core.cache import cache
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.core.exceptions import ObjectDoesNotExist
from courses.models import Course, Enrollment
from courses.serializers import CourseSerializer, EnrollmentSerializer
from users.permissions import IsAdmin,IsStudent

import logging

logger = logging.getLogger('app_logger')

class CourseViewSet(viewsets.ModelViewSet):
    """
    Handles operations related to courses.
    Includes caching for the course list and admin-only permissions for specific actions.
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['instructor', 'name']
    
    def get_permissions(self):
        """
        Set admin permissions for create, update, and destroy actions.
        """
        if self.action in ['create', 'update', 'destroy']:
            self.permission_classes = [IsAuthenticated, IsAdmin]
        return super().get_permissions()
    
    def list(self, request, *args, **kwargs):
        """
        Override the list method to add caching for the courses list.
        """
        cache_key = "courses_list"
        cached_data = cache.get(cache_key)

        if cached_data:
            logger.info("Cache hit for courses list")
            return Response(cached_data, status=status.HTTP_200_OK)

        logger.info("Cache miss for courses list")
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        cache.set(cache_key, serializer.data, timeout=3600)  # Cache for 1 hour
        return Response(serializer.data)

    def perform_create(self, serializer):
        """
        Clear cache when a course is created.
        """
        instance = serializer.save()
        cache.delete("courses_list")
        logger.info("Cache invalidated after creating a course")
        return instance

    def perform_update(self, serializer):
        """
        Clear cache when a course is updated.
        """
        instance = serializer.save()
        cache.delete("courses_list")
        logger.info("Cache invalidated after updating a course")
        return instance

    def perform_destroy(self, instance):
        """
        Clear cache when a course is deleted.
        """
        super().perform_destroy(instance)
        cache.delete("courses_list")
        logger.info("Cache invalidated after deleting a course")


class EnrollmentViewSet(viewsets.ModelViewSet):
    """
    Handles operations related to enrollments with role-based permissions.
    Includes logging for key actions.
    """
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer

    def get_permissions(self):
        """
        Assign permissions based on the action:
        - Admin permissions for create, update, and delete actions.
        - Student and Admin permissions for list and retrieve actions.
        """
        if self.action in ['create', 'update', 'destroy']:
            self.permission_classes = [IsAdmin]
        else:  # list, retrieve
            self.permission_classes = [IsStudent | IsAdmin]
        return super().get_permissions()

    def get_queryset(self):
        """
        Return enrollments based on the user's role.
        """
        user = self.request.user

        if hasattr(user, 'student'):
            logger.info(f"Student {user.username} is retrieving their enrollments.")
            return self.queryset.filter(student__user=user)
        
        logger.info(f"Admin {user.username} is retrieving all enrollments.")
        return super().get_queryset()

    def perform_create(self, serializer):
        """
        Handle creation of enrollments with logging.
        """
        user = self.request.user
        if hasattr(user, 'student'):
            student = user.student
            serializer.save(student=student)
            logger.info(f"Student {user.username} enrolled in course {serializer.validated_data['course']}.")
        else:
            instance = serializer.save()
            logger.info(f"Admin {user.username} created an enrollment for student {instance.student} in course {instance.course}.")

    def destroy(self, request, *args, **kwargs):
        """
        Handle deletion of enrollments with logging.
        """
        instance = self.get_object()
        logger.info(f"User {request.user.username} deleted enrollment ID {instance.id}.")
        return super().destroy(request, *args, **kwargs)
