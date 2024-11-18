import logging
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Grade
from .serializers import GradeSerializer
from users.permissions import IsStudent, IsTeacher, IsAdmin
from courses.models import Course

# Configure logger
logger = logging.getLogger('app_logger')


class GradeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing grades:
    - Students: View only their grades.
    - Teachers: View and manage grades for courses they teach.
    - Admins: Full access to all grades.
    """
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    permission_classes = [IsAuthenticated]  # Base permission

    def get_permissions(self):
        """
        Assign specific permissions based on the action.
        """
        logger.info(f"Assigning permissions for action: {self.action}")
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsTeacher() | IsAdmin()]  # Only teachers or admins can modify grades
        elif self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]  # Allow authenticated users to view
        return super().get_permissions()

    def get_queryset(self):
        """
        Filter the grades based on the user's role.
        """
        user = self.request.user
        logger.info(f"Fetching grades for user: {user}")

        if IsStudent().has_permission(self.request, self):
            logger.info(f"User {user} is a student. Returning their grades.")
            return Grade.objects.filter(student__user=user)

        elif IsTeacher().has_permission(self.request, self):
            logger.info(f"User {user} is a teacher. Returning grades for their courses.")
            return Grade.objects.filter(course__professor=user)

        elif IsAdmin().has_permission(self.request, self):
            logger.info(f"User {user} is an admin. Returning all grades.")
            return Grade.objects.all()

        logger.warning(f"User {user} does not have access to any grades.")
        return Grade.objects.none()

    def create(self, request, *args, **kwargs):
        """
        Teachers can create grades for students in their courses.
        """
        user = request.user
        logger.info(f"User {user} is attempting to create a grade.")

        # Ensure the user is a teacher
        if not IsTeacher().has_permission(request, self):
            logger.error(f"User {user} is not authorized to create grades.")
            return Response(
                {"error": "Only teachers can create grades."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Validate the course
        data = request.data
        try:
            course = Course.objects.get(id=data['course'])
        except Course.DoesNotExist:
            logger.error(f"Course with id {data['course']} not found.")
            return Response(
                {"error": "Invalid course ID."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if course.professor != user:
            logger.error(f"User {user} does not teach the course {course}.")
            return Response(
                {"error": "You can only grade students in courses you teach."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Proceed with grade creation
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        grade = serializer.save()
        logger.info(f"Grade created successfully: {grade}")
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """
        Log grade updates.
        """
        logger.info(f"User {self.request.user} is attempting to update a grade.")
        response = super().update(request, *args, **kwargs)
        logger.info(f"Grade updated successfully. Data: {response.data}")
        return response

    def destroy(self, request, *args, **kwargs):
        """
        Log grade deletions.
        """
        logger.info(f"User {self.request.user} is attempting to delete a grade.")
        grade = self.get_object()
        super().destroy(request, *args, **kwargs)
        logger.info(f"Grade deleted successfully: {grade}")
        return Response({"message": "Grade deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
