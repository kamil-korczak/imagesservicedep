from django.urls import include, path, re_path
from . import views


UUID4_REGEX = '[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}'

urlpatterns = [
    path("api/", include("imagesservice.api.urls")),
    re_path(rf"img/(?P<image_id>{UUID4_REGEX})/", views.serve_image, name="serve_image"),
    re_path(rf"img/thumb/(?P<image_id>{UUID4_REGEX})/", views.serve_thumbnail_image, name="serve_thumbnail_image"),
    re_path(rf"img/temp/(?P<image_id>{UUID4_REGEX})/", views.serve_temp_image, name="serve_temp_image"),
]
