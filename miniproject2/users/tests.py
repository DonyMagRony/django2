# users/tests/test_users.py
import pytest
from rest_framework.test import APIClient
from users.models import User
from users.serializers import CustomUserCreateSerializer, CustomUserSerializer

@pytest.mark.django_db
def test_user_creation():
    user = User.objects.create_user(username="testuser", password="password", role="student")
    assert user.username == "testuser"
    assert user.role == "student"
    assert user.check_password("password")

@pytest.mark.django_db
def test_user_create_serializer():
    data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "securepassword123",
        "role": "teacher"
    }
    serializer = CustomUserCreateSerializer(data=data)
    assert serializer.is_valid()
    user = serializer.save()
    assert user.username == "newuser"
    assert user.email == "newuser@example.com"
    assert user.role == "teacher"

@pytest.mark.django_db
def test_user_serializer():
    user = User(username="existinguser", email="existinguser@example.com", role="admin")
    serializer = CustomUserSerializer(user)
    expected_data = {
        "id": user.id,
        "username": "existinguser",
        "email": "existinguser@example.com",
        "role": "admin"
    }
    assert serializer.data == expected_data

@pytest.mark.django_db
def test_register_user():
    client = APIClient()
    data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "securepassword",
        "role": "student"
    }
    response = client.post("/usersregister/", data)  # Corrected URL
    assert response.status_code == 201
    assert response.data["username"] == "testuser"
 
@pytest.mark.django_db
def test_update_user_role_as_admin():
    client = APIClient()
    admin_user = User.objects.create_superuser(username="admin", password="adminpass", role="admin")
    client.force_authenticate(user=admin_user)

    user = User.objects.create_user(username="testuser", password="password", role="student")
    response = client.patch(f"/users{user.id}/role/", {"role": "teacher"})
    assert response.status_code == 200
    assert response.data["message"] == "Role updated successfully"
    user.refresh_from_db()

@pytest.mark.django_db
def test_update_user_role_as_non_admin():
    client = APIClient()
    non_admin_user = User.objects.create_user(username="regularuser", password="password", role="student")
    client.force_authenticate(user=non_admin_user)

    user = User.objects.create_user(username="testuser", password="password", role="student")
    response = client.patch(f"/users{user.id}/role/", {"role": "teacher"})
    assert response.status_code == 403  # Forbidden

@pytest.mark.django_db
def test_admin_can_access_update_role():
    client = APIClient()
    admin_user = User.objects.create_superuser(username="admin", password="adminpass", role="admin")
    client.force_authenticate(user=admin_user)
    response = client.patch("/users1/role/", {"role": "teacher"})
    assert response.status_code != 403

@pytest.mark.django_db
def test_non_admin_cannot_access_update_role():
    client = APIClient()
    non_admin_user = User.objects.create_user(username="user", password="userpass", role="student")
    client.force_authenticate(user=non_admin_user)
    response = client.patch("/users1/role/", {"role": "teacher"})
    assert response.status_code == 403

