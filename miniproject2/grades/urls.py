from rest_framework.routers import DefaultRouter
from .views import GradeViewSet

router = DefaultRouter()
router.register('', GradeViewSet, basename='grade')  # No prefix

urlpatterns = router.urls