from datetime import date
import pytest
from unittest import mock
from attendance.models import Attendance
from courses.models import Course
from grades.models import Grade
from notifications.tasks import daily_report_summary, notify_grade_update, send_daily_attendance_reminder, weekly_performance_summary
from students.models import Student
from users.models import User  # Import User model


@pytest.mark.django_db
@mock.patch('notifications.tasks.send_mail')
def test_send_daily_attendance_reminder(mock_send_mail):
    """
    Test that the send_daily_attendance_reminder task sends emails to all students.
    """
    # Arrange: Create a test User and Student
    user = User.objects.create(username='testuser', email='student@example.com', password='testpassword')
    student = Student.objects.create(user=user, dob='2000-01-01')  # Link to the User

    # Act: Trigger the Celery task directly
    send_daily_attendance_reminder()

    # Assert: Verify that send_mail was called with the correct parameters
    mock_send_mail.assert_called_once_with(
        subject='Daily Attendance Reminder',
        message='Please remember to mark your attendance today.',
        from_email='admin@school.com',
        recipient_list=[student.user.email]  # Fetch email from the User model
    )

@pytest.mark.django_db
@mock.patch('notifications.tasks.send_mail')
def test_notify_grade_update(mock_send_mail):
    """
    Test that the notify_grade_update task sends an email when a student's grade is updated.
    """
    # Arrange: Create a student and a grade update
    user = User.objects.create(username='testuser', email='student@example.com', password='testpassword')
    student = Student.objects.create(user=user, dob='2000-01-01')# Link to the User
    course = Course.objects.create(name='Math', description='Mathematics course', professor=user)
    grade = Grade.objects.create(student=student, course=course, grade=85.0)

    # Act: Trigger the Celery task directly
    notify_grade_update(student, course.name, grade.grade)

    # Assert: Verify that send_mail was called with the correct parameters
    mock_send_mail.assert_called_once_with(
        subject='Grade Update Notification',
        message=f'Your grade for Math has been updated to: 85.0.',
        from_email='admin@school.com',
        recipient_list=[student.user.email]  # Access email from the related User model
    )

@pytest.mark.django_db
@mock.patch('notifications.tasks.send_mail')
def test_daily_report_summary(mock_send_mail):
    """
    Test that the daily_report_summary task sends a summary email with attendance and grade updates.
    """
    # Arrange: Create attendance and grade records for today
    today = date.today()
    user = User.objects.create(username='testuser', email='student@example.com', password='testpassword')
    student = Student.objects.create(user=user, dob='2000-01-01')  # Link to the User
    course = Course.objects.create(name='Math', description='Mathematics course', professor=user)
    
    # Create attendance and grade records
    Attendance.objects.create(student=student, course=course, date=today)
    Grade.objects.create(student=student, course=course, grade=85.0, date=today)

    # Act: Trigger the Celery task directly
    daily_report_summary()

    # Assert: Verify that send_mail was called with the correct parameters
    mock_send_mail.assert_called_once_with(
        subject='Daily Report Summary',
        message=(
            "Attendance records added today: 1\n"
            "Grades updated today: 1"
        ),
        from_email='admin@school.com',
        recipient_list=['admin@school.com'],
    )



@pytest.mark.django_db
@mock.patch('notifications.tasks.send_mail')
def test_weekly_performance_summary(mock_send_mail):
    """
    Test that the weekly_performance_summary task sends emails to all students with their grades and attendance.
    """
    # Arrange: Create a student, course, grades, and attendance records
    user = User.objects.create(username='testuser', email='student@example.com', password='testpassword')
    student = Student.objects.create(user=user, dob='2000-01-01')
    course = Course.objects.create(name='Math', description='Mathematics course', professor=user)
    
    # Add grade and attendance records for the student
    Grade.objects.create(student=student, course=course, grade=90.0)
    Attendance.objects.create(student=student, course=course, date=date.today(), status='Present')

    # Act: Trigger the Celery task
    weekly_performance_summary()

    # Assert: Verify that send_mail was called with the correct parameters
    mock_send_mail.assert_called_once_with(
        subject='Weekly Performance Summary',
        message=(
            f"Your grades:\n[{{'course__name': 'Math', 'grade': 90.0}}]\n"
            f"Your attendance:\n[{{'date': '{date.today()}', 'status': 'Present'}}]"
        ),
        from_email='admin@school.com',
        recipient_list=['student@example.com'],
    )