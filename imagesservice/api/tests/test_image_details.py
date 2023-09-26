import pytest
from django.urls import reverse
from pytest_drf import (APIViewTest, UsesGetMethod, UsesPatchMethod, Returns403)
from .config import ENTERPRISE_IMAGE_ID, IMAGE_FOREST, IMAGE_TOO_SMALL
from .schemas.image_details import IMAGE_DETAILS_BASIC_SCHEMA, IMAGE_DETAILS_PREMIUM_SCHEMA, IMAGE_DETAILS_ENTERPRISE_SCHEMA
from rest_framework import status


class TestGetNotAuthenticated(
    APIViewTest,
    UsesGetMethod,
    Returns403
    ):

    @pytest.fixture
    def url(self):
        return reverse('Image-detail', args={"pk": ENTERPRISE_IMAGE_ID})


class TestPutNotAuthenticated(
    APIViewTest,
    UsesPatchMethod,
    Returns403
    ):

    @pytest.fixture
    def url(self):
        return reverse('Image-detail', args={"pk": ENTERPRISE_IMAGE_ID})


@pytest.mark.django_db
class TestGetImage:

    def test_basic_account(self, authenticated_client__basic_account, basic_image_url):
        response = authenticated_client__basic_account.get(basic_image_url, format='json')
        assert response.status_code == status.HTTP_200_OK
        response_json = response.json()
        assert 'image_url' not in response_json
        assert 'expiring_images' not in response_json
        assert IMAGE_DETAILS_BASIC_SCHEMA.validate(response_json)

    def test_premium_account(self, authenticated_client__premium_account, premium_image_url):
        response = authenticated_client__premium_account.get(premium_image_url, format='json')
        assert response.status_code == status.HTTP_200_OK
        response_json = response.json()
        assert 'expiring_images' not in response_json
        assert IMAGE_DETAILS_PREMIUM_SCHEMA.validate(response_json)

    def test_enterprise_account(self, authenticated_client__enterprise_account, enterprise_image_url):
        response = authenticated_client__enterprise_account.get(enterprise_image_url, format='json')
        assert response.status_code == status.HTTP_200_OK
        response_json = response.json()
        assert IMAGE_DETAILS_ENTERPRISE_SCHEMA.validate(response_json)

    def test_against_image_of_other_user(self, authenticated_client__basic_account, enterprise_image_url):
        response = authenticated_client__basic_account.get(enterprise_image_url, format='json')
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestPatchImage:
    def test_basic_account(self, authenticated_client__basic_account, basic_image_url):
        with open(IMAGE_FOREST, 'rb') as fp:
            data = {"filename": fp}
            response = authenticated_client__basic_account.patch(basic_image_url, format='multipart', data=data)
            assert response.status_code == status.HTTP_200_OK

    def test_basic_account_with_too_small_image(self, authenticated_client__basic_account, basic_image_url):
        with open(IMAGE_TOO_SMALL, 'rb') as fp:
            data = {"filename": fp}
            response = authenticated_client__basic_account.patch(basic_image_url, format='multipart', data=data)
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert response.json()['filename'] == ['Image height must be at least 400 px, current have 113 px.']

    def test_against_image_of_other_user(self, authenticated_client__basic_account, enterprise_image_url):
        response = authenticated_client__basic_account.patch(enterprise_image_url, format='json')
        assert response.status_code == status.HTTP_404_NOT_FOUND
