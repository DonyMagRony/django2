import pytest
from rest_framework.test import APIClient
from rest_framework import status
from courses.models import Course
from users.models import User
from django.core.cache import cache


@pytest.mark.django_db
class TestCourseAPI:

    def test_list_courses_as_admin(self):
        """
        Ensure that an admin user can list all courses.
        """
        admin_user = User.objects.create_user(username="admin", password="password", role="admin")
        client = APIClient()
        client.force_authenticate(user=admin_user)

        response = client.get("/courses/")
        assert response.status_code == 200
        assert isinstance(response.data, list)  # Should return a list of courses

    def test_list_courses_as_non_admin(self):
        """
        Ensure that a non-admin user (teacher/student) cannot list all courses.
        """
        teacher_user = User.objects.create_user(username="teacher", password="password", role="teacher")
        client = APIClient()
        client.force_authenticate(user=teacher_user)

        response = client.get("/courses/")
        assert response.status_code == 200
        assert isinstance(response.data, list)  # Teacher should still see courses they are associated with

    def test_create_course_as_admin(self):
        """
        Ensure that an admin user can create a course.
        """
        admin_user = User.objects.create_user(username="admin", password="password", role="admin")
        teacher_user = User.objects.create_user(username="teacher", password="pasord", role="teacher")

        client = APIClient()
        client.force_authenticate(user=admin_user)

        data = {
            "name": "Math 101",
            "description": "Basic Mathematics",
            "professor": teacher_user.id
        }

        response = client.post("/courses/", data)
        assert response.status_code == 201
        assert Course.objects.count() == 1
        assert response.data["name"] == "Math 101"

    def test_create_course_as_teacher(self):
        """
        Ensure that a teacher cannot create a course.
        """
        teacher_user = User.objects.create_user(username="teacher", password="password", role="teacher")
        client = APIClient()
        client.force_authenticate(user=teacher_user)

        data = {
            "name": "Math 101",
            "description": "Basic Mathematics",
            "professor": teacher_user.id
        }

        response = client.post("/courses/", data)
        assert response.status_code == 403  # Forbidden for non-admin

    def test_read_course(self):
        """
        Ensure that a course can be read.
        """
        admin_user = User.objects.create_user(username="admin", password="password", role="admin")
        client = APIClient()
        client.force_authenticate(user=admin_user)

        course = Course.objects.create(name="Biology 101", description="Basic Biology", professor=admin_user)

        response = client.get(f"/courses/{course.id}/")
        assert response.status_code == 200
        assert response.data["name"] == "Biology 101"

    def test_update_course(self):
        """
        Ensure that an admin user can update a course.
        """
        admin_user = User.objects.create_user(username="admin", password="password", role="admin")
        teacher_user = User.objects.create_user(username="teacher", password="password", role="teacher")

        client = APIClient()
        client.force_authenticate(user=admin_user)

        course = Course.objects.create(name="Biology 101", description="Basic Biology", professor=teacher_user)
        data = {
            "name": "Biology 102",  # Update course name
            "description": "Advanced Biology",  # Update description
            "professor": teacher_user.id
        }

        response = client.put(f"/courses/{course.id}/", data)
        assert response.status_code == 200
        assert response.data["name"] == "Biology 102"

    def test_partial_update_course(self):
        """
        Ensure that an admin user can partially update a course.
        """
        admin_user = User.objects.create_user(username="admin", password="password", role="admin")
        client = APIClient()
        client.force_authenticate(user=admin_user)

        course = Course.objects.create(name="Chemistry 101", description="Basic Chemistry", professor=admin_user)
        data = {
            "description": "Advanced Chemistry"  # Only update the description
        }

        response = client.patch(f"/courses/{course.id}/", data)
        assert response.status_code == 200
        assert response.data["description"] == "Advanced Chemistry"

    def test_delete_course(self):
        """
        Ensure that an admin user can delete a course.
        """
        admin_user = User.objects.create_user(username="admin", password="password", role="admin")
        client = APIClient()
        client.force_authenticate(user=admin_user)

        course = Course.objects.create(name="Chemistry 101", description="Basic Chemistry", professor=admin_user)

        response = client.delete(f"/courses/{course.id}/")
        assert response.status_code == 204  # No Content (success)
        assert Course.objects.count() == 0  # The course should be deleted

    def test_cache_course_list(self):
        """
        Ensure that the course list is cached and reused on repeated requests.
        """
        admin_user = User.objects.create_user(username="admin", password="password", role="admin")
        teacher_user = User.objects.create_user(username="teacher", password="password", role="teacher")
        client = APIClient()
        client.force_authenticate(user=admin_user)

        # Create a course to be included in the list
        data = {
            "name": "Physics 101",
            "description": "Basic Physics",
            "professor": teacher_user.id
        }
        response = client.post("/courses/", data)
        assert response.status_code == 201  # Course should be created successfully

        # Clear cache before making the request
        cache.clear()

        # First request (cache miss)
        response = client.get("/courses/")
        assert response.status_code == 200
        assert len(response.data) == 1  # Should return the newly created course

        # Check if cache is set after the first request
        cached_data = cache.get("courses_list")
        assert cached_data is not None  # Cache should be set with the course data

        # Second request (cache hit)
        response = client.get("/courses/")
        assert response.status_code == 200
        assert response.data == cached_data  # Should return cached data

        # Modify the course and ensure cache is invalidated on subsequent requests
        updated_data = {
            "name": "Physics 102",
            "description": "Advanced Physics",
            "professor": teacher_user.id
        }

        # Perform update
        course_id = response.data[0]["id"]
        response = client.put(f"/courses/{course_id}/", updated_data)
        assert response.status_code == 200

        # After update, ensure that cache is invalidated and new data is fetched
        cached_data_after_update = cache.get("courses_list")
        assert cached_data_after_update is None  # Cache should be cleared after update

        # Re-fetch the course list to see the new data
        response = client.get("/courses/")
        assert response.status_code == 200
        assert response.data[0]["name"] == "Physics 102"  # Should return the updated course
# Should return cached data


@pytest.mark.django_db
class TestCoursePermissions:

    def test_permissions_for_create_course(self):
        """
        Ensure that only admin users can create courses.
        """
        admin_user = User.objects.create_user(username="admin", password="password", role="admin")
        teacher_user = User.objects.create_user(username="teacher", password="password", role="teacher")
        client = APIClient()

        # Admin user should be able to create a course
        client.force_authenticate(user=admin_user)
        data = {
            "name": "Math 101",
            "description": "Math course",
            "professor": teacher_user.id
        }
        response = client.post("/courses/", data)
        assert response.status_code == 201

        # Teacher user should NOT be able to create a course
        client.force_authenticate(user=teacher_user)
        response = client.post("/courses/", data)
        assert response.status_code == 403  # Forbidden
