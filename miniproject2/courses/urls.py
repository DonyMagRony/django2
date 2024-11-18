from rest_framework.routers import DefaultRouter
from .views import CourseViewSet

router = DefaultRouter()
router.register('', CourseViewSet, basename='course')  # No prefix

urlpatterns = router.urls
