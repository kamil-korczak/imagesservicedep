import pytest
from pytest_drf import APIViewTest, UsesGetMethod, UsesPostMethod, Returns403
from rest_framework import status
from imagesservice.models import ExpiringImage
from imagesservice.api.tests.schemas.expiring_images_list import EXPIRING_IMAGE_DETAILS_ENTERPRISE_SCHEMA
from imagesservice.config import EXPIRE_AFTER_MIN, EXPIRE_AFTER_MAX


@pytest.mark.django_db
class TestGetNotAuthenticated(
    APIViewTest,
    UsesGetMethod,
    Returns403
    ):

    @pytest.fixture
    def url(self, enterprise_expiring_image_detail_url):
        return enterprise_expiring_image_detail_url


@pytest.mark.django_db
class TestPostNotAuthenticated(
    APIViewTest,
    UsesPostMethod,
    Returns403
    ):

    @pytest.fixture
    def url(self, enterprise_expiring_image_detail_url):
        return enterprise_expiring_image_detail_url


@pytest.mark.django_db
class TestGetExpiringImageDetail:

    @pytest.mark.parametrize('authenticated_client, image_url', [
        ('authenticated_client__premium_account', 'enterprise_expiring_image_detail_url'),
        ('authenticated_client__basic_account', 'enterprise_expiring_image_detail_url'),
    ])
    def test_accounts_with_image_not_belongs_to_account(self, authenticated_client, image_url, request):
        authenticated_client = request.getfixturevalue(authenticated_client)
        image_url = request.getfixturevalue(image_url)
        response = authenticated_client.get(image_url, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_enterprise_account_with_image_belongs_to_account(self, create_test_expiring_image,
                                                              authenticated_client__enterprise_account,
                                                              enterprise_expiring_image_detail_url):
        response = authenticated_client__enterprise_account.get(enterprise_expiring_image_detail_url, format='json')
        response_json = response.json()
        assert response.status_code == status.HTTP_200_OK
        assert EXPIRING_IMAGE_DETAILS_ENTERPRISE_SCHEMA.validate(response_json)
        assert response_json['id'] == str(create_test_expiring_image.id)
        assert response_json['expire_after'] == create_test_expiring_image.expire_after


@pytest.mark.django_db
class TestPatchExpiringImage:

    @pytest.mark.parametrize('raw_authenticated_client, image_url', [
        ('authenticated_client__premium_account', 'enterprise_expiring_image_detail_url'),
        ('authenticated_client__basic_account', 'enterprise_expiring_image_detail_url'),
    ])
    def test_accounts_with_image_belongs_to_other_account(self, raw_authenticated_client, image_url, request):
        authenticated_client = request.getfixturevalue(raw_authenticated_client)
        image_url = request.getfixturevalue(image_url)
        response = authenticated_client.post(image_url, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_enterprise_account_with_image_belongs_to_account(self, authenticated_client__enterprise_account, enterprise_expiring_image_detail_url):
        expire_after = 7000
        data = dict(expire_after=expire_after)
        response = authenticated_client__enterprise_account.patch(enterprise_expiring_image_detail_url, format='json', data=data)
        response_json = response.json()
        assert response.status_code == status.HTTP_200_OK
        assert response_json['expire_after'] == expire_after
        expiring_images = ExpiringImage.objects.filter(image_id=response_json['image_id'])
        assert expiring_images.count() == 1

    def test_enterprise_account_with_image_belongs_to_account_expire_after_too_small(
            self, authenticated_client__enterprise_account, enterprise_expiring_image_detail_url):
        data = {'expire_after': EXPIRE_AFTER_MIN-10}
        response = authenticated_client__enterprise_account.patch(enterprise_expiring_image_detail_url, format='json', data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {'expire_after': [f'Ensure this value is greater than or equal to {EXPIRE_AFTER_MIN}.']}

    def test_enterprise_account_with_image_belongs_to_account_expire_after_too_big(
            self, authenticated_client__enterprise_account, enterprise_expiring_image_detail_url):
        data = {'expire_after': EXPIRE_AFTER_MAX+10}
        response = authenticated_client__enterprise_account.patch(enterprise_expiring_image_detail_url, format='json', data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {'expire_after': [f'Ensure this value is less than or equal to {EXPIRE_AFTER_MAX}.']}
