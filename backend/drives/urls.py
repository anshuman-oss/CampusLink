from rest_framework.routers import DefaultRouter
from .views import DriveViewSet
router = DefaultRouter()
router.register("", DriveViewSet, basename="drives")
urlpatterns = router.urls