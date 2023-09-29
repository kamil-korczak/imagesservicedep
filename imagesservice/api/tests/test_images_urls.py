import pytest
from django.urls import reverse
from imagesservice.config import UPGRADE_ACCOUNT_TIER_MESSAGE
from .config import BASIC_IMAGE_ID, BASIC_THUMBNAIL_IMAGE_400_ID, PREMIUM_EXPIRING_IMAGE_ID
from rest_framework import status


@pytest.mark.django_db
class TestImageURLAccess:

    # NOTE: The tests of existing images are done after the image-list POST.

    def test_image_from_basic_account_access_forbidden(self, client):
        response = client.get(reverse('serve_image', kwargs={'image_id': BASIC_IMAGE_ID}))
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.content == bytes(UPGRADE_ACCOUNT_TIER_MESSAGE, "utf-8")

    def test_image_from_premium_account_not_found(self, client):
        response = client.get(reverse('serve_image', kwargs={'image_id': PREMIUM_EXPIRING_IMAGE_ID}))
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestExpiringImageURLAccess:

    # NOTE: The tests of existing expiring-images are done after the expiring-image-list POST.

    def test_image_from_basic_account_not_found(self, client):
        response = client.get(reverse('serve_temp_image', kwargs={'image_id': BASIC_IMAGE_ID}))
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_image_from_premium_account_access_forbidden(self, client):
        response = client.get(reverse('serve_temp_image', kwargs={'image_id': PREMIUM_EXPIRING_IMAGE_ID}))
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.content == bytes(UPGRADE_ACCOUNT_TIER_MESSAGE, "utf-8")


@pytest.mark.django_db
class TestThumbnailImageURLAccess:

    # NOTE: The tests of existing thumbnails are done after the image-list POST.

    def test_image_from_basic_account_access_forbidden(self, client):
        response = client.get(reverse('serve_thumbnail_image', kwargs={'image_id': BASIC_THUMBNAIL_IMAGE_400_ID}))
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.content == bytes(UPGRADE_ACCOUNT_TIER_MESSAGE, "utf-8")

    def test_image_on_premium_account_from_other_account_access_forbidden(self, client):
        response = client.get(reverse('serve_thumbnail_image', kwargs={'image_id': BASIC_THUMBNAIL_IMAGE_400_ID}))
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.content == bytes(UPGRADE_ACCOUNT_TIER_MESSAGE, "utf-8")
