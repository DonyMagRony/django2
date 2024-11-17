from rest_framework.permissions import BasePermission

class IsTeacher(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'teacher'
    
class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'admin'
