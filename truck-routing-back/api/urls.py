from rest_framework.routers import DefaultRouter
from api.views import TripViewSet, RouteViewSet, CheckpointViewSet

router = DefaultRouter()

router.register("trips", TripViewSet, basename="trip")
router.register("routes", RouteViewSet, basename="route")
router.register(
    "checkpoints",
    CheckpointViewSet,
    basename="checkpoint",
)

urlpatterns = router.urls
