from django.urls import path, include
from rest_framework.routers import DefaultRouter
from attendance.views import AttendanceViewSet, MarkAttendanceView

# Set up the router for AttendanceViewSet
router = DefaultRouter()
router.register(r'attendance', AttendanceViewSet, basename='attendance')

urlpatterns = [
    # Include all routes generated by the router
    path('', include(router.urls)),

    # Custom URL for marking attendance
    path(
        'attendance/mark/<int:student_id>/<int:course_id>/',
        MarkAttendanceView.as_view(),
        name='mark-attendance'
    ),
]
