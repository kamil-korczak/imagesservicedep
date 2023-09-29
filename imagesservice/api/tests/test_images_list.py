import pytest
from django.urls import reverse
from rest_framework import status
from pytest_drf import APIViewTest, UsesGetMethod, UsesPostMethod, Returns403
from .schemas.images_list import IMAGES_LIST_BASIC_SCHEMA, IMAGES_LIST_PREMIUM_SCHEMA, IMAGES_LIST_ENTERPRISE_SCHEMA
from .config import (IMAGE_PARK, IMAGE_TOO_SMALL, RANDOM_FILE, BASIC_ALLOWED_THUMBNAIL_HEIGHTS,
                     PREMIUM_ALLOWED_THUMBNAIL_HEIGHTS, ENTERPRISE_ALLOWED_THUMBNAIL_HEIGHTS)
from ...models import Image


class TestGetNotAuthenticated(
    APIViewTest,
    UsesGetMethod,
    Returns403
    ):

    @pytest.fixture
    def url(self):
        return reverse('Image-list')


class TestPostNotAuthenticated(
    APIViewTest,
    UsesPostMethod,
    Returns403
    ):

    @pytest.fixture
    def url(self):
        return reverse('Image-list')


@pytest.mark.django_db
class TestGetImagesList:

    def test_basic_account(self, authenticated_client__basic_account, images_url):
        response = authenticated_client__basic_account.get(images_url, format='json')
        assert response.status_code == status.HTTP_200_OK
        response_json = response.json()
        assert response_json['count'] == 1
        assert 'image_url' not in response_json
        assert 'expiring_images' not in response_json
        assert IMAGES_LIST_BASIC_SCHEMA.validate(response_json)

    def test_premium_account(self, authenticated_client__premium_account, images_url):
        response = authenticated_client__premium_account.get(images_url, format='json')
        assert response.status_code == status.HTTP_200_OK
        response_json = response.json()
        assert response_json['count'] == 1
        assert 'expiring_images' not in response_json
        assert IMAGES_LIST_PREMIUM_SCHEMA.validate(response_json)

    def test_enterprise_account(self, authenticated_client__enterprise_account, images_url):
        response = authenticated_client__enterprise_account.get(images_url, format='json')
        assert response.status_code == status.HTTP_200_OK
        response_json = response.json()
        assert response_json['count'] == 1
        assert IMAGES_LIST_ENTERPRISE_SCHEMA.validate(response_json)


@pytest.mark.django_db
class TestPostImagesList:

    def test_basic_without_file(self, authenticated_client__basic_account, images_url):
        response = authenticated_client__basic_account.post(images_url, format='multipart')
        response_json = response.json()
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response_json == {'filename': ['No file was submitted.']}

    def test_basic_with_wrong_file(self, authenticated_client__basic_account, images_url):
        with open(RANDOM_FILE, 'rb') as fp:
            data = dict(filename=fp)
            response = authenticated_client__basic_account.post(images_url, format='multipart', data=data)
        response_json = response.json()
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response_json == {'filename': ['Upload a valid image. The file you uploaded was either not an image or a corrupted image.']}

    def test_basic_with_too_small_image(self, authenticated_client__basic_account, images_url):
        with open(IMAGE_TOO_SMALL, 'rb') as fp:
            data = dict(filename=fp)
            response = authenticated_client__basic_account.post(images_url, format='multipart', data=data)
        response_json = response.json()
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response_json == {'filename': ['Image height must be at least 400 px, current have 113 px.']}

    def test_basic_account(self, client, authenticated_client__basic_account, images_url):
        with open(IMAGE_PARK, 'rb') as fp:
            data = dict(filename=fp)
            response = authenticated_client__basic_account.post(images_url, format='multipart', data=data)
        response_json = response.json()
        image_id = response_json['id']
        assert response.status_code == status.HTTP_201_CREATED
        assert client.get(reverse('serve_image', kwargs={"image_id": image_id})).status_code == status.HTTP_403_FORBIDDEN
        assert len(response_json['thumbnail_images']) == len(BASIC_ALLOWED_THUMBNAIL_HEIGHTS)
        for thumbnail in response_json['thumbnail_images']:
            assert thumbnail['height'] in BASIC_ALLOWED_THUMBNAIL_HEIGHTS
            assert client.get(reverse('serve_thumbnail_image', kwargs={"image_id": thumbnail['id']})).status_code == status.HTTP_200_OK
            assert client.get(thumbnail['image_url']).status_code == status.HTTP_200_OK
        Image.objects.get(id=image_id)

    def test_premium_account(self, client, authenticated_client__premium_account, images_url):
        with open(IMAGE_PARK, 'rb') as fp:
            data = dict(filename=fp)
            response = authenticated_client__premium_account.post(images_url, format='multipart', data=data)
        response_json = response.json()
        image_id = response_json['id']
        assert response.status_code == status.HTTP_201_CREATED
        assert client.get(reverse('serve_image', kwargs={"image_id": image_id})).status_code == status.HTTP_200_OK
        assert client.get(response_json['image_url']).status_code == status.HTTP_200_OK
        assert len(response_json['thumbnail_images']) == len(PREMIUM_ALLOWED_THUMBNAIL_HEIGHTS)
        for thumbnail in response_json['thumbnail_images']:
            assert thumbnail['height'] in PREMIUM_ALLOWED_THUMBNAIL_HEIGHTS
            assert client.get(reverse('serve_thumbnail_image', kwargs={"image_id": thumbnail['id']})).status_code == status.HTTP_200_OK
            assert client.get(thumbnail['image_url']).status_code == status.HTTP_200_OK
        Image.objects.get(id=image_id)

    def test_enterprise_account(self, client, authenticated_client__enterprise_account, images_url):
        with open(IMAGE_PARK, 'rb') as fp:
            data = dict(filename=fp)
            response = authenticated_client__enterprise_account.post(images_url, format='multipart', data=data)
        response_json = response.json()
        image_id = response_json['id']
        assert client.get(reverse('serve_image', kwargs={"image_id": image_id})).status_code == status.HTTP_200_OK
        assert client.get(response_json['image_url']).status_code == status.HTTP_200_OK
        assert response.status_code == status.HTTP_201_CREATED
        assert len(response_json['thumbnail_images']) == len(ENTERPRISE_ALLOWED_THUMBNAIL_HEIGHTS)
        for thumbnail in response_json['thumbnail_images']:
            assert thumbnail['height'] in ENTERPRISE_ALLOWED_THUMBNAIL_HEIGHTS
            assert client.get(reverse('serve_thumbnail_image', kwargs={"image_id": thumbnail['id']})).status_code == status.HTTP_200_OK
            assert client.get(thumbnail['image_url']).status_code == status.HTTP_200_OK
        Image.objects.get(id=image_id)
