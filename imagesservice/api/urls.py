from django.urls import include, path
from rest_framework import routers
from . import views


router = routers.DefaultRouter()
router.register(r'images', views.ImageViewSet, basename="Image")
router.register(r'images/(?P<image_id>[^/.]+)/expiring-images', views.ExpiringImageViewSet, basename="ExpiringImage")


urlpatterns = [
    path("", include(router.urls)),
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
]
