from django.test import TestCase
from rest_framework.test import APIClient,APITestCase
from rest_framework import status
from users.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from students.models import Student
from courses.models import Course
from grades.models import Grade
from users.models import User
from rest_framework_simplejwt.tokens import RefreshToken
import json


class GradeModelTest(TestCase):
    def setUp(self):
        # Set up the test data
        self.user = User.objects.create(username='testuser', email='student@example.com', password='testpassword',role="student")
        self.student = Student.objects.create(user=self.user, dob='2000-01-01')  
        self.admin_user = User.objects.create_user(username="admin", password="password", role="admin")
        self.teacher_user = User.objects.create_user(username="teacher", password="password", role="teacher")
        self.course = Course.objects.create(name="Test Course", description="Test Course Description", professor=self.teacher_user)
        self.grade = Grade.objects.create(student=self.student, course=self.course, grade=90.0)

    def test_grade_validation(self):
        """Test that grade is between 0 and 100."""
        invalid_grade = Grade(student=self.student, course=self.course, grade=105.0)
        with self.assertRaises(ValidationError):
            invalid_grade.full_clean()  # Trigger validation

    def test_grade_string_representation(self):
        """Test the string representation of the grade."""
        self.assertEqual(str(self.grade), f"{self.student.user.username} - {self.course.name} - {self.grade.grade}")


class GradeAPITestCase(APITestCase):
    def setUp(self):
        # Set up the test data
        self.student_user = User.objects.create_user(
            username='student', email='student@example.com', password='studentpassword', role="student", is_active=True
        )
        self.student = Student.objects.create(user=self.student_user, dob='2000-01-01')
        
        self.admin_user = User.objects.create_user(
            username="admin", email="admin@example.com", password="adminpassword", role="admin", is_active=True
        )
        
        self.teacher_user = User.objects.create_user(
            username="teacher", email="teacher@example.com", password="teacherpassword", role="teacher", is_active=True
        )
        
        self.course = Course.objects.create(name="Test Course", description="Test Course Description", professor=self.teacher_user)
        self.grade = Grade.objects.create(student=self.student, course=self.course, grade=90.0)

        # Initialize API client
        self.client = APIClient()

    def get_authentication_headers(self, user):
        """Helper method to get auth headers for a user using Djoser JWT."""
        login_response = self.client.post('/auth/jwt/create/', {
            'username': user.username,
            'password': 'studentpassword' if user == self.student_user else 'adminpassword' if user == self.admin_user else 'teacherpassword',
        })

        # Debugging response
        print("Login Response:", login_response.data)

        # Check if the 'access' token exists
        if 'access' not in login_response.data:
            raise Exception(f"Failed to obtain access token for {user.role}: {login_response.data}")

        # Return the headers for authorization
        return {'Authorization': f"Bearer {login_response.data['access']}"}

    def test_grade_create_teacher(self):
        """Test that a teacher can create a grade."""
        data = {'student': self.student.id, 'course': self.course.id, 'grade': 95.0}
        headers = self.get_authentication_headers(self.teacher_user)
        response = self.client.post('/api/grades/', data, format='json', **headers)

        # Assert the grade was successfully created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Parse and validate response data
        response_data = json.loads(response.content)
        self.assertEqual(response_data['student'], self.student.id)
        self.assertEqual(response_data['course'], self.course.id)
        self.assertEqual(response_data['grade'], 95.0)

    def test_grade_create_student(self):
        """Test that a student cannot create a grade."""
        data = {'student': self.student.id, 'course': self.course.id, 'grade': 95.0}
        headers = self.get_authentication_headers(self.student_user)
        response = self.client.post('/api/grades/', data, format='json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_grade_create_admin(self):
        """Test that an admin can create a grade."""
        data = {'student': self.student.id, 'course': self.course.id, 'grade': 95.0}
        headers = self.get_authentication_headers(self.admin_user)
        response = self.client.post('/api/grades/', data, format='json', **headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_grade_update_teacher(self):
        """Test that a teacher can update a grade."""
        data = {'grade': 98.0}
        self.client.credentials(**self.get_authentication_headers(self.teacher_user))
        response = self.client.patch(f'/grades/{self.grade.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.grade.refresh_from_db()
        self.assertEqual(self.grade.grade, 98.0)

    def test_grade_update_student(self):
        """Test that a student cannot update a grade."""
        data = {'grade': 98.0}
        self.client.credentials(**self.get_authentication_headers(self.student_user))
        response = self.client.patch(f'/grades/{self.grade.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_grade_update_admin(self):
        """Test that an admin can update a grade."""
        data = {'grade': 98.0}
        self.client.credentials(**self.get_authentication_headers(self.admin_user))
        response = self.client.patch(f'/grades/{self.grade.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.grade.refresh_from_db()
        self.assertEqual(self.grade.grade, 98.0)

    def test_grade_delete_teacher(self):
        """Test that a teacher can delete a grade."""
        self.client.credentials(**self.get_authentication_headers(self.teacher_user))
        response = self.client.delete(f'/grades/{self.grade.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_grade_delete_student(self):
        """Test that a student cannot delete a grade."""
        self.client.credentials(**self.get_authentication_headers(self.student_user))
        response = self.client.delete(f'/grades/{self.grade.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_grade_delete_admin(self):
        """Test that an admin can delete a grade."""
        self.client.credentials(**self.get_authentication_headers(self.admin_user))
        response = self.client.delete(f'/grades/{self.grade.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_grade_list_student(self):
        """Test that a student can list their grades."""
        self.client.credentials(**self.get_authentication_headers(self.student_user))
        response = self.client.get('/grades/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Student should only see their grade

    def test_grade_list_teacher(self):
        """Test that a teacher can list grades for their course."""
        self.client.credentials(**self.get_authentication_headers(self.teacher_user))
        response = self.client.get('/grades/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)  # Teacher should see grades for their course

    def test_grade_list_admin(self):
        """Test that an admin can list all grades."""
        self.client.credentials(**self.get_authentication_headers(self.admin_user))
        response = self.client.get('/grades/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)  # Admin should see all grades

