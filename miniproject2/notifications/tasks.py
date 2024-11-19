"""
Tasks for the notifications app.

This module contains background tasks for sending notifications and generating periodic reports.

Tasks:
- send_daily_attendance_reminder: Sends a reminder to students for daily attendance.
- notify_grade_update: Notifies students when their grade is updated.
- daily_report_summary: Sends a daily summary report to the admin.
- weekly_performance_summary: Sends a weekly performance summary to students.
"""

from celery import shared_task
from django.core.mail import send_mail
from datetime import date
from attendance.models import Attendance
from grades.models import Grade
from students.models import Student

@shared_task
def send_daily_attendance_reminder():
    """
    Sends a daily reminder email to all students to mark their attendance.

    This task is executed every day using Celery Beat.
    """
    students = Student.objects.select_related('user').all()  # Optimize query with select_related
    for student in students:
        send_mail(
            subject='Daily Attendance Reminder',
            message='Please remember to mark your attendance today.',
            from_email='admin@school.com',
            recipient_list=[student.user.email],  # Fetch email from the related User
        )



@shared_task
def notify_grade_update(student, course_name, grade):
    """
    Sends an email notification to a student when their grade is updated.

    Args:
        student_id (int): ID of the student to notify.
        course_name (str): Name of the course.
        grade (str): Updated grade for the course.
    """
    student = Student.objects.get(id=student.id)
    send_mail(
        subject='Grade Update Notification',
        message=f'Your grade for {course_name} has been updated to: {grade}.',
        from_email='admin@school.com',
        recipient_list=[student.user.email],
    )



@shared_task
def daily_report_summary():
    """
    Sends a daily summary report of attendance and grades to the admin.
    This task is executed every day using Celery Beat.
    """
    today = date.today()
    attendance_count = Attendance.objects.filter(date=today).count()
    grade_updates = Grade.objects.filter(date=today).count()

    send_mail(
        subject='Daily Report Summary',
        message=(
            f"Attendance records added today: {attendance_count}\n"
            f"Grades updated today: {grade_updates}"
        ),
        from_email='admin@school.com',
        recipient_list=['admin@school.com'],
    )



@shared_task
def weekly_performance_summary():
    """
    Sends a weekly performance summary email to all students.
    This task is executed every week using Celery Beat.
    """
    students = Student.objects.all()
    for student in students:
        grades = Grade.objects.filter(student=student)
        attendance = Attendance.objects.filter(student=student)

        # Format date explicitly for consistency
        attendance_data = list(attendance.values('date', 'status'))
        for record in attendance_data:
            record['date'] = record['date'].strftime('%Y-%m-%d')  # Format date as string

        send_mail(
            subject='Weekly Performance Summary',
            message=(
                f"Your grades:\n{list(grades.values('course__name', 'grade'))}\n"
                f"Your attendance:\n{attendance_data}"
            ),
            from_email='admin@school.com',
            recipient_list=[student.user.email],
        )
