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
from django.urls import reverse

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
            username="admin", email="admin@example.com", password="adminpassword", role="admin", is_active=True,is_staff=True
        )
        
        self.teacher_user = User.objects.create_user(
            username="teacher", email="teacher@example.com", password="teacherpassword", role="teacher", is_active=True
        )
        
        self.course = Course.objects.create(name="Test Course", description="Test Course Description", professor=self.teacher_user)
        self.grade = Grade.objects.create(student=self.student, course=self.course, grade=90.0)

        # Initialize API client
        self.client = APIClient()

    def get_authentication_headers(self, user):
        """Helper method to get authorization headers for a user."""
        login_data = {
            'username': user.username,
            'password': 'studentpassword' if user == self.student_user else 'adminpassword' if user == self.admin_user else 'teacherpassword',
        }
    
        response = self.client.post("/auth/jwt/create/", data=login_data)
  
        access_token = response.data['access']
        return {'HTTP_AUTHORIZATION': f'Bearer {access_token}'}


    def test_grade_create_teacher(self):
        """Test that a teacher can authenticate and create a grade."""
        # Step 1: Authenticate and get headers
        headers = self.get_authentication_headers(self.teacher_user)
        
        # Assert that headers contain the authorization token
        self.assertIn('HTTP_AUTHORIZATION', headers, "Authentication headers not returned.")

        # Step 2: Verify token works by accessing a protected endpoint
        protected_url = reverse('grade-list')  # Assuming this endpoint requires authentication
        response = self.client.get(protected_url, **headers)
        self.assertNotEqual(response.status_code, 401, "Authentication failed: Unauthorized access.")

        # Step 3: Attempt to create a grade
        data = {'student': self.student.id, 'course': self.course.id, 'grade': 95.0}
        response = self.client.post(protected_url, data, format='json', **headers)

        # Assert that the grade was successfully created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, "Grade creation failed.")
        self.assertEqual(response.data['grade'], data['grade'], "The grade value does not match.")
        self.assertEqual(response.data['student'], data['student'], "The student value does not match.")
        self.assertEqual(response.data['course'], data['course'], "The course value does not match.")

    def test_grade_create_student(self):
            """Test that a student cannot create a grade."""
            data = {'student': self.student.id, 'course': self.course.id, 'grade': 95.0}
            headers = self.get_authentication_headers(self.student_user)
            response = self.client.post(reverse('grade-list'), data, format='json', **headers)
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_grade_create_admin(self):
        headers = self.get_authentication_headers(self.admin_user)
        
        # Assert that headers contain the authorization token
        self.assertIn('HTTP_AUTHORIZATION', headers, "Authentication headers not returned.")

        # Step 2: Verify token works by accessing a protected endpoint
        protected_url = reverse('grade-list')  # Assuming this endpoint requires authentication
        response = self.client.get(protected_url, **headers)
        self.assertNotEqual(response.status_code, 401, "Authentication failed: Unauthorized access.")

        # Step 3: Attempt to create a grade
        data = {'student': self.student.id, 'course': self.course.id, 'grade': 95.0}
        response = self.client.post(protected_url, data, format='json', **headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, "Grade creation failed.")
        self.assertEqual(response.data['grade'], data['grade'], "The grade value does not match.")
        self.assertEqual(response.data['student'], data['student'], "The student value does not match.")
        self.assertEqual(response.data['course'], data['course'], "The course value does not match.")

        
    def test_grade_update_teacher(self):
        """Test that a teacher can update a grade."""
        data = {'grade': 98.0}
        headers = self.get_authentication_headers(self.teacher_user)
        response = self.client.patch(reverse('grade-detail', args=[self.grade.id]), data, format='json', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.grade.refresh_from_db()
        self.assertEqual(self.grade.grade, 98.0)

    def test_grade_update_student(self):
        """Test that a student cannot update a grade."""
        data = {'grade': 98.0}
        headers = self.get_authentication_headers(self.student_user)
        response = self.client.patch(reverse('grade-detail', args=[self.grade.id]), data, format='json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_grade_update_admin(self):
        """Test that an admin can update a grade."""
        data = {'grade': 98.0}
        headers = self.get_authentication_headers(self.admin_user)
        response = self.client.patch(reverse('grade-detail', args=[self.grade.id]), data, format='json', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.grade.refresh_from_db()
        self.assertEqual(self.grade.grade, 98.0)

    def test_grade_delete_teacher(self):
        """Test that a teacher can delete a grade."""
        headers = self.get_authentication_headers(self.teacher_user)
        response = self.client.delete(reverse('grade-detail', args=[self.grade.id]), **headers)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_grade_delete_student(self):
        """Test that a student cannot delete a grade."""
        headers = self.get_authentication_headers(self.student_user)
        response = self.client.delete(reverse('grade-detail', args=[self.grade.id]), **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_grade_delete_admin(self):
        """Test that an admin can delete a grade."""
        headers = self.get_authentication_headers(self.admin_user)
        response = self.client.delete(reverse('grade-detail', args=[self.grade.id]), **headers)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_grade_list_student(self):
        """Test that a student can list their grades."""
        headers = self.get_authentication_headers(self.student_user)
        response = self.client.get(reverse('grade-list'), **headers)
        print(f"Student Grades: {response.data}")  # Debugging line to see the actual response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Assert the student can only see their grades
        student_grades = [grade for grade in response.data['results'] if grade['student'] == self.student_user.id]
        self.assertGreater(len(student_grades), 0)  # Student should see at least their grade

    def test_grade_list_teacher(self):
        """Test that a teacher can list grades for their courses."""
        # Get authentication headers for the teacher
        headers = self.get_authentication_headers(self.teacher_user)
        
        # Perform a GET request to the grade list endpoint
        response = self.client.get(reverse('grade-list'), **headers)
        
        # Check the response status is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Get all grades from the response
        grades = response.data.get('results', [])
        
        # Check if all returned grades belong to the teacher's courses
        teacher_courses = {course.id for course in Course.objects.filter(professor=self.teacher_user)}
        grades_for_teacher_courses = [
            grade for grade in grades if grade['course'] in teacher_courses
        ]
        
        # Assert that there are grades returned for the teacher's courses
        self.assertGreater(len(grades_for_teacher_courses), 0, "Teacher should see grades for their courses.")
        
        # Ensure all returned grades belong to the teacher's courses
        for grade in grades_for_teacher_courses:
            self.assertIn(grade['course'], teacher_courses, f"Grade {grade['id']} does not belong to the teacher's courses.")

    def test_grade_list_admin(self):
        """Test that an admin can list all grades."""
        headers = self.get_authentication_headers(self.admin_user)
        response = self.client.get(reverse('grade-list'), **headers)
        print(f"Admin Grades: {response.data}")  # Debugging line to see the actual response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Admin should see all grades
        self.assertGreater(len(response.data), 0)  # Admin should see at least one grade