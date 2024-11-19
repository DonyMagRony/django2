from djoser.serializers import UserCreateSerializer, UserSerializer
from .models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth import password_validation
from rest_framework import serializers


class CustomUserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'role']

    def validate_password(self, value):
        """
        Validate the password using Django's password validators.
        """
        password_validation.validate_password(value)
        return value

    def create(self, validated_data):
        """
        Hash the password and create a new user instance.
        """
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)  # Hash the password
        user.save()
        return user
    
class CustomUserSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        model = User
        fields = ['id', 'username', 'email', 'role']  # Include additional fields
