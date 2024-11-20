from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import UserActivity, CoursePopularity
from django.db.models import Count
from django.core.cache import cache
from rest_framework import status

@api_view(['GET'])
def active_users(request):
    """
    View to display the most active users based on total API requests.
    Returns data in JSON format.
    """
    try:
        users = UserActivity.objects.annotate(request_count=Count('total_requests')).order_by('-request_count')
        if not users:
            return Response({"message": "No active users found."}, status=status.HTTP_404_NOT_FOUND)
    except UserActivity.DoesNotExist:
        return Response({"message": "User activity data is unavailable."}, status=status.HTTP_404_NOT_FOUND)
    
    # Prepare the response data
    user_data = [{"username": user.user.username, "total_requests": user.request_count} for user in users]
    
    return Response({"active_users": user_data}, status=status.HTTP_200_OK)


@api_view(['GET'])
def popular_courses(request):
    """
    View to display the most popular courses based on views.
    Returns data in JSON format.
    """
    # Try to retrieve cached data for popular courses
    courses = cache.get('popular_courses')
    
    if not courses:
        # If data is not cached, fetch from the database
        try:
            courses = CoursePopularity.objects.order_by('-views')
            if not courses:
                return Response({"message": "No popular courses found."}, status=status.HTTP_404_NOT_FOUND)
            
            # Cache the courses for 15 minutes
            cache.set('popular_courses', courses, timeout=60 * 15)
        except CoursePopularity.DoesNotExist:
            return Response({"message": "Course popularity data is unavailable."}, status=status.HTTP_404_NOT_FOUND)
    
    # Prepare the response data
    course_data = [{"course_name": course.course.name, "views": course.views} for course in courses]
    
    return Response({"popular_courses": course_data}, status=status.HTTP_200_OK)
