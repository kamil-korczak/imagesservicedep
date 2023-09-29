import pytest
from pytest_drf import APIViewTest, UsesGetMethod, UsesPostMethod, Returns403
from rest_framework import status
from django.urls import reverse
from imagesservice.models import ExpiringImage
from imagesservice.api.tests.schemas.expiring_images_list import EXPIRING_IMAGES_LIST_ENTERPRISE_SCHEMA
from imagesservice.config import EXPIRE_AFTER_MIN, EXPIRE_AFTER_MAX


class TestGetNotAuthenticated(
    APIViewTest,
    UsesGetMethod,
    Returns403
    ):

    @pytest.fixture
    def url(self, enterprise_expiring_image_list_url):
        return enterprise_expiring_image_list_url


class TestPostNotAuthenticated(
    APIViewTest,
    UsesPostMethod,
    Returns403
    ):

    @pytest.fixture
    def url(self, enterprise_expiring_image_list_url):
        return enterprise_expiring_image_list_url


@pytest.mark.django_db
class TestGetExpiringImageList:

    @pytest.mark.parametrize('raw_authenticated_client, image_url', [
        ('authenticated_client__premium_account', 'premium_expiring_image_list_url'),
        ('authenticated_client__basic_account', 'basic_expiring_image_list_url'),
    ])
    def test_accounts_with_image_belongs_to_account(self, raw_authenticated_client, image_url, request):
        authenticated_client = request.getfixturevalue(raw_authenticated_client)
        image_url = request.getfixturevalue(image_url)
        response = authenticated_client.get(image_url, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_enterprise_account_with_image_belongs_to_account(self, authenticated_client__enterprise_account,
                                                              enterprise_expiring_image_list_url, create_test_expiring_image):
        response = authenticated_client__enterprise_account.get(enterprise_expiring_image_list_url, format='json')
        response_json = response.json()
        assert response.status_code == status.HTTP_200_OK
        assert EXPIRING_IMAGES_LIST_ENTERPRISE_SCHEMA.validate(response_json)


@pytest.mark.django_db
class TestPostExpiringImage:

    @pytest.mark.parametrize('raw_authenticated_client, image_url', [
        ('authenticated_client__premium_account', 'premium_expiring_image_list_url'),
        ('authenticated_client__basic_account', 'basic_expiring_image_list_url'),
    ])
    def test_accounts_with_image_belongs_to_account(self, raw_authenticated_client, image_url, request):
        authenticated_client = request.getfixturevalue(raw_authenticated_client)
        image_url = request.getfixturevalue(image_url)
        response = authenticated_client.post(image_url, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.parametrize('raw_authenticated_client, image_url', [
        ('authenticated_client__basic_account', 'enterprise_expiring_image_list_url'),
        ('authenticated_client__enterprise_account', 'basic_expiring_image_list_url'),
    ])
    def test_with_image_from_other_account(self, raw_authenticated_client, image_url, request):
        authenticated_client = request.getfixturevalue(raw_authenticated_client)
        image_url = request.getfixturevalue(image_url)
        response = authenticated_client.post(image_url, format='json')
        response_json = response.json()
        if raw_authenticated_client.endswith('enterprise_account'):
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert response_json == {'image_id': ["Image doesn't exist"], 'expire_after': ['This field is required.']}
        else:
            assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_enterprise_account_with_image_belongs_to_account_expire_after_required(
            self, authenticated_client__enterprise_account, enterprise_expiring_image_list_url):
        response = authenticated_client__enterprise_account.post(enterprise_expiring_image_list_url, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {'expire_after': ['This field is required.']}

    def test_enterprise_account_with_image_belongs_to_account_expire_after_too_small(
            self, authenticated_client__enterprise_account, enterprise_expiring_image_list_url):
        data = {'expire_after': EXPIRE_AFTER_MIN - 10}
        response = authenticated_client__enterprise_account.post(enterprise_expiring_image_list_url, format='json', data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {'expire_after': [f'Ensure this value is greater than or equal to {EXPIRE_AFTER_MIN}.']}

    def test_enterprise_account_with_image_belongs_to_account_expire_after_too_big(
            self, authenticated_client__enterprise_account, enterprise_expiring_image_list_url):
        data = {'expire_after': EXPIRE_AFTER_MAX + 10}
        response = authenticated_client__enterprise_account.post(enterprise_expiring_image_list_url, format='json', data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {'expire_after': [f'Ensure this value is less than or equal to {EXPIRE_AFTER_MAX}.']}

    def test_enterprise_account_with_image_belongs_to_account(self, client, authenticated_client__enterprise_account,
                                                              enterprise_expiring_image_list_url, copy_enterprise_image):
        data = {'expire_after': EXPIRE_AFTER_MAX}
        response = authenticated_client__enterprise_account.post(enterprise_expiring_image_list_url, format='json', data=data)
        expiring_image_id = response.json()['id']
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()['expire_after'] == EXPIRE_AFTER_MAX
        assert client.get(reverse('serve_temp_image', kwargs={'image_id': expiring_image_id})).status_code == status.HTTP_200_OK
        ExpiringImage.objects.get(id=expiring_image_id)
