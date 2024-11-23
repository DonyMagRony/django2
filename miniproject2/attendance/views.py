import logging
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from attendance.models import Attendance
from attendance.serializers import AttendanceSerializer
from users.permissions import IsStudent, IsTeacher, IsAdmin
from students.models import Student
from courses.models import Course, Enrollment

# Set up a logger
logger = logging.getLogger('app_logger')

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class AttendanceViewSet(viewsets.ModelViewSet):
    """
    Viewset for admins and teachers to view, create, update, and delete attendance.
    """
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'update', 'destroy']:
            logger.info(f"User {self.request.user} attempting to {self.action} attendance.")
            return [IsTeacher()]
        return [IsAdmin()]  # Allow Admins to do everything

    def get_queryset(self):
        if self.request.user.role == 'teacher':
            logger.info(f"Teacher {self.request.user} retrieving attendance for their courses.")
            return Attendance.objects.filter(course__professor=self.request.user)
        logger.info(f"Admin {self.request.user} retrieving all attendance records.")
        return Attendance.objects.all()

    @swagger_auto_schema(
        operation_description="Retrieve a list of all attendance records.",
        responses={200: AttendanceSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Create a new attendance record.",
        request_body=AttendanceSerializer,
        responses={201: AttendanceSerializer},
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Update an existing attendance record.",
        request_body=AttendanceSerializer,
        responses={200: AttendanceSerializer},
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Delete an attendance record.",
        responses={204: "No Content"},
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)



class MarkAttendanceView(APIView):
    """
    A custom view for students to mark their attendance (only "present" or "absent").
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Mark attendance for a specific course and date.",
        manual_parameters=[
            openapi.Parameter(
                'student_id', openapi.IN_PATH, description="ID of the student", type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'course_id', openapi.IN_PATH, description="ID of the course", type=openapi.TYPE_INTEGER
            ),
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'date': openapi.Schema(type=openapi.TYPE_STRING, format='date', description='Date for attendance'),
                'status': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    enum=['present', 'absent'],
                    description="Attendance status ('present' or 'absent')"
                ),
            },
            required=['date', 'status']
        ),
        responses={
            200: openapi.Response("Attendance marked successfully."),
            400: "Invalid status.",
            403: "Unauthorized access.",
            404: "Student or course not found.",
        },
    )
    def post(self, request, student_id, course_id):
        """
        Students can mark their own attendance for a specific course and date.
        """
        try:
            logger.info(f"Student {request.user} is attempting to mark attendance for course {course_id}.")

            # Ensure the logged-in user is the student trying to mark their attendance
            if request.user.id != student_id:
                logger.warning(f"Unauthorized access: User {request.user} tried to mark attendance for student {student_id}.")
                return Response(
                    {"error": "You can only mark your own attendance."},
                    status=status.HTTP_403_FORBIDDEN
                )

            # Ensure the student exists
            student = Student.objects.get(id=student_id)

            # Ensure the course exists
            course = Course.objects.get(id=course_id)

            # Verify the student is enrolled in the course
            if not Enrollment.objects.filter(student=student, course=course).exists():
                logger.warning(f"Enrollment check failed: Student {student_id} is not enrolled in course {course_id}.")
                return Response(
                    {"error": "You are not enrolled in this course."},
                    status=status.HTTP_403_FORBIDDEN
                )

            # Check if attendance already exists for today; if so, update it
            attendance, created = Attendance.objects.get_or_create(
                student=student,
                course=course,
                date=request.data.get("date"),  # Date should be passed in the request body
            )

            # Validate and update attendance status (only 'present' or 'absent' allowed)
            status_value = request.data.get("status")
            if status_value not in ['present', 'absent']:
                logger.error(f"Invalid status value '{status_value}' provided by student {student_id}.")
                return Response(
                    {"error": "Invalid status. Please choose 'present' or 'absent'."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            attendance.status = status_value
            attendance.save()

            logger.info(f"Attendance marked: Student {student_id} marked as {status_value} for course {course_id}.")
            return Response(
                {"message": f"Attendance marked as {status_value}.", "attendance_id": attendance.id},
                status=status.HTTP_200_OK
            )

        except Student.DoesNotExist:
            logger.error(f"Student {student_id} does not exist.")
            return Response(
                {"error": "Student not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Course.DoesNotExist:
            logger.error(f"Course {course_id} does not exist.")
            return Response(
                {"error": "Course not found."},
                status=status.HTTP_404_NOT_FOUND
            )
