from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from attendance.models import Attendance
from students.models import Student
from courses.models import Course, Enrollment
from django.contrib.auth.models import User

class AttendanceTests(APITestCase):

    def setUp(self):
        # Create users
        self.student_user = User.objects.create_user(username='student1', password='testpass', is_staff=False)
        self.teacher_user = User.objects.create_user(username='teacher1', password='testpass', is_staff=True)
        self.admin_user = User.objects.create_superuser(username='admin1', password='testpass')

        # Create a student, teacher, and course
        self.student = Student.objects.create(user=self.student_user, name="Student One")
        self.teacher = self.teacher_user  # Assuming teacher directly linked as a user
        self.course = Course.objects.create(name="Math 101", professor=self.teacher_user)

        # Enroll student in the course
        Enrollment.objects.create(student=self.student, course=self.course)

        # Login clients
        self.student_client = APIClient()
        self.student_client.login(username='student1', password='testpass')

        self.teacher_client = APIClient()
        self.teacher_client.login(username='teacher1', password='testpass')

        self.admin_client = APIClient()
        self.admin_client.login(username='admin1', password='testpass')

    def test_student_mark_attendance(self):
        url = reverse('mark-attendance', args=[self.student.id, self.course.id])
        data = {"date": "2024-11-21", "status": "present"}
        response = self.student_client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Attendance marked as present.")

    def test_student_mark_unauthorized(self):
        # Attempt to mark attendance for another student
        url = reverse('mark-attendance', args=[999, self.course.id])  # Non-existent student ID
        data = {"date": "2024-11-21", "status": "present"}
        response = self.student_client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_teacher_access_attendance(self):
        url = reverse('attendance-list')  # Assuming attendance viewset uses a route
        response = self.teacher_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_status(self):
        url = reverse('mark-attendance', args=[self.student.id, self.course.id])
        data = {"date": "2024-11-21", "status": "unknown"}  # Invalid status
        response = self.student_client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_admin_create_attendance(self):
        url = reverse('attendance-list')
        data = {
            "student": self.student.id,
            "course": self.course.id,
            "date": "2024-11-21",
            "status": "present"
        }
        response = self.admin_client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
