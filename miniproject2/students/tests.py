import pytest
from rest_framework.test import APIClient
from users.models import User
from students.models import Student

@pytest.mark.django_db
def test_student_creation():
    user = User.objects.create_user(username="studentuser", password="password", role="student")
    student = Student.objects.create(user=user, dob="2000-01-01")
    assert student.user.username == "studentuser"
    assert student.dob == "2000-01-01"

@pytest.mark.django_db
def test_student_list_view_as_admin():
    client = APIClient()
    admin_user = User.objects.create_superuser(username="admin", password="adminpass", role="admin")
    client.force_authenticate(user=admin_user)

    user1 = User.objects.create_user(username="student1", password="password", role="student")
    user2 = User.objects.create_user(username="student2", password="password", role="student")
    Student.objects.create(user=user1, dob="2001-01-01")
    Student.objects.create(user=user2, dob="2002-02-02")

    response = client.get("/students/")
    assert response.status_code == 200
    assert len(response.data) == 2

@pytest.mark.django_db
def test_student_retrieve_view():
    client = APIClient()
    user = User.objects.create_user(username="teststudent", password="password", role="student")
    student = Student.objects.create(user=user, dob="1995-05-05")
    client.force_authenticate(user=user)

    response = client.get(f"/students/{student.id}/")
    assert response.status_code == 200
    assert response.data["user"] == user.id
    assert response.data["dob"] == "1995-05-05"

@pytest.mark.django_db
def test_student_update_view():
    client = APIClient()
    user = User.objects.create_user(username="teststudent", password="password", role="student")
    student = Student.objects.create(user=user, dob="1995-05-05")
    client.force_authenticate(user=user)

    updated_data = {"dob": "1996-06-06"}
    response = client.patch(f"/students/{student.id}/", data=updated_data)
    assert response.status_code == 200

    student.refresh_from_db()
    assert student.dob == "1996-06-06"

@pytest.mark.django_db
def test_student_creation_as_admin():
    client = APIClient()
    admin_user = User.objects.create_superuser(username="admin", password="adminpass", role="admin")
    client.force_authenticate(user=admin_user)

    user = User.objects.create_user(username="newstudent", password="password", role="student")
    data = {"user": user.id, "dob": "2000-01-01"}
    response = client.post("/students/", data=data)
    assert response.status_code == 201
    assert response.data["dob"] == "2000-01-01"

@pytest.mark.django_db
def test_student_access_as_non_authenticated():
    client = APIClient()
    user = User.objects.create_user(username="teststudent", password="password", role="student")
    student = Student.objects.create(user=user, dob="1995-05-05")

    response = client.get(f"/students/{student.id}/")
    assert response.status_code == 401  # Unauthorized
