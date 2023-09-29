import os
import shutil
import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from django.conf import settings
from django.urls import reverse
from django.test import Client
from .config import BASIC_IMAGE_ID, PREMIUM_IMAGE_ID, ENTERPRISE_IMAGE_ID, IMAGE_PARK_WITH_ROAD
from ...models import Image, ExpiringImage


@pytest.fixture(scope="session", autouse=True)
def cleanup_media_root(request):
    media_root = settings.TEST_MEDIA_ROOT
    yield
    if os.path.exists(media_root):
        shutil.rmtree(media_root)


@pytest.fixture
def create_test_expiring_image():
    expiring_image = ExpiringImage.objects.create(image=Image(id=ENTERPRISE_IMAGE_ID), expire_after=3500)
    yield expiring_image


def copy_image(image_id: str):
    image = Image.objects.get(id=image_id)
    test_media_root = settings.MEDIA_ROOT
    destination = f"{test_media_root}/{image.filename}"
    os.makedirs(os.path.dirname(destination), exist_ok=True)
    shutil.copyfile(f"{IMAGE_PARK_WITH_ROAD}", destination)


@pytest.fixture
def copy_enterprise_image():
    copy_image(image_id=ENTERPRISE_IMAGE_ID)
    yield


@pytest.fixture
def client():
    c = Client()
    yield c


def authenticated_client(username, request):
    user = User.objects.get(username=username)
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def authenticated_client__basic_account(request):
    username = "testb"
    yield authenticated_client(username, request)


@pytest.fixture
def authenticated_client__premium_account(request):
    username = "testp"
    yield authenticated_client(username, request)


@pytest.fixture
def authenticated_client__enterprise_account(request):
    username = "teste"
    yield authenticated_client(username, request)


@pytest.fixture
def images_url(request):
    return reverse('Image-list')


@pytest.fixture
def basic_image_url(request):
    return reverse('Image-detail', kwargs={"pk": BASIC_IMAGE_ID})


@pytest.fixture
def premium_image_url(request):
    return reverse('Image-detail', kwargs={"pk": PREMIUM_IMAGE_ID})


@pytest.fixture
def enterprise_image_url(request):
    return reverse('Image-detail', kwargs={"pk": ENTERPRISE_IMAGE_ID})


@pytest.fixture
def basic_expiring_image_list_url(request):
    return reverse('ExpiringImage-list', kwargs={"image_id": BASIC_IMAGE_ID})


@pytest.fixture
def premium_expiring_image_list_url(request):
    return reverse('ExpiringImage-list', kwargs={"image_id": PREMIUM_IMAGE_ID})


@pytest.fixture
def enterprise_expiring_image_list_url(request):
    return reverse('ExpiringImage-list', kwargs={"image_id": ENTERPRISE_IMAGE_ID})


@pytest.fixture
def enterprise_expiring_image_detail_url(request, create_test_expiring_image):
    return reverse('ExpiringImage-detail', kwargs={"image_id": ENTERPRISE_IMAGE_ID, "pk": str(create_test_expiring_image.id)})
