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
from drf_yasg.utils import swagger_auto_schema
from analytics.models import CourseMetric


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
    filterset_fields = ['professor', 'name']
    
    def get_permissions(self):
        """
        Set admin permissions for create, update, and destroy actions.
        """
        if self.action in ['create', 'update', 'destroy']:
            self.permission_classes = [IsAuthenticated, IsAdmin]
        return super().get_permissions()
    

    @swagger_auto_schema(
        operation_summary="List all courses",
        operation_description="Retrieve a list of courses, with caching enabled to improve performance.",
        responses={200: CourseSerializer(many=True)}
    )
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

    @swagger_auto_schema(
        operation_summary="Create a course",
        operation_description="Create a new course. Only accessible to admin users.",
        responses={
            201: CourseSerializer,
            403: "Forbidden: Admin permission required."
        }
    )
    def perform_create(self, serializer):
        """
        Clear cache when a course is created.
        """
        instance = serializer.save()
        cache.delete("courses_list")
        logger.info("Cache invalidated after creating a course")
        return instance

    @swagger_auto_schema(
        operation_summary="Update a course",
        operation_description="Update an existing course. Only accessible to admin users.",
        responses={
            200: CourseSerializer,
            403: "Forbidden: Admin permission required.",
            404: "Not Found"
        }
    )
    def perform_update(self, serializer):
        """
        Clear cache when a course is updated.
        """
        instance = serializer.save()
        cache.delete("courses_list")
        logger.info("Cache invalidated after updating a course")
        return instance

    @swagger_auto_schema(
        operation_summary="Delete a course",
        operation_description="Delete a course. Only accessible to admin users.",
        responses={
            204: "No Content",
            403: "Forbidden: Admin permission required.",
            404: "Not Found"
        }
    )
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
    permission_classes = [IsAuthenticated]

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

    @swagger_auto_schema(
        operation_summary="List enrollments",
        operation_description="Retrieve a list of enrollments. Admins can view all, students can view their own.",
        responses={200: EnrollmentSerializer(many=True)}
    )
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
    
    @swagger_auto_schema(
        operation_summary="Create an enrollment",
        operation_description="Create a new enrollment. Students can enroll themselves, and admins can create enrollments for any student.",
        responses={
            201: EnrollmentSerializer,
            403: "Forbidden: Permission denied."
        }
    )
    
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


    @swagger_auto_schema(
        operation_summary="Retrieve an enrollment",
        operation_description="Retrieve the details of a specific enrollment. Admins can access all, students can access their own.",
        responses={
            200: EnrollmentSerializer,
            403: "Forbidden: Permission denied.",
            404: "Not Found"
        }
    )
    def retrieve(self, request, *args, **kwargs):
        course = self.get_object()
        metric, created = CourseMetric.objects.using('analytics').get_or_create(course=course)
        metric.views += 1
        metric.save(using='analytics')
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create an enrollment",
        operation_description="Create a new enrollment. Students can enroll themselves, and admins can create enrollments for any student.",
        responses={
            201: EnrollmentSerializer,
            403: "Forbidden: Permission denied."
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update an enrollment",
        operation_description="Update an existing enrollment. Only accessible to admin users.",
        responses={
            200: EnrollmentSerializer,
            403: "Forbidden: Admin permission required.",
            404: "Not Found"
        }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete an enrollment",
        operation_description="Delete an enrollment. Only accessible to admin users.",
        responses={
            204: "No Content",
            403: "Forbidden: Admin permission required.",
            404: "Not Found"
        }
    )
    def destroy(self, request, *args, **kwargs):
        """
        Handle deletion of enrollments with logging.
        """
        instance = self.get_object()
        logger.info(f"User {request.user.username} deleted enrollment ID {instance.id}.")
        return super().destroy(request, *args, **kwargs)
