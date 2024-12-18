from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from users.serializers import CustomUserSerializer
from .models import User
from djoser.views import UserViewSet  # Import the Djoser UserViewSet
from drf_yasg.utils import swagger_auto_schema

import logging
logger = logging.getLogger('app_logger')  # Use the custom logger defined in settings

class CustomUserViewSet(UserViewSet):   
    serializer_class = CustomUserSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        logger.info(f"New user registered: {user.username} (ID: {user.id})")
        super().perform_create(serializer)

class UpdateRoleView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    @swagger_auto_schema(
        operation_description="Update a user's role. Only admin users can perform this action.",
        responses={
            200: "Role updated successfully.",
            400: "Role is already set to the requested value.",
            404: "User not found."
        }
    )

    def patch(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
            old_role = user.role
            new_role = request.data.get('role')

            if old_role == new_role:
                return Response(
                    {"message": "Role is already set to the requested value"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            user.role = new_role
            user.save()
            logger.info(f"User role updated: {user.username} (ID: {user.id}) - {old_role} → {new_role}")
            return Response({"message": "Role updated successfully"}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            logger.error(f"Attempted to update role for non-existent user (ID: {pk})")
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
