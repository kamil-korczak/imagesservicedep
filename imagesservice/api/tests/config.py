import os
from django.conf import settings


BASIC_ALLOWED_THUMBNAIL_HEIGHTS = [200]
PREMIUM_ALLOWED_THUMBNAIL_HEIGHTS = [200, 400]
ENTERPRISE_ALLOWED_THUMBNAIL_HEIGHTS = [200, 400]

BASIC_IMAGE_ID = "75830a27-82c5-4907-8c48-3caeed50a77d"
PREMIUM_IMAGE_ID = "498b26c1-a363-4ea7-932a-57ac78c75812"
ENTERPRISE_IMAGE_ID = "c5f43fee-a9d0-444f-97b8-3fa35e06d4a3"

IMAGE_FOREST = os.path.join(settings.BASE_DIR, 'imagesservice/api/tests/data/images/forest.jpg')
IMAGE_PARK = os.path.join(settings.BASE_DIR, 'imagesservice/api/tests/data/images/park.jpg')
RANDOM_FILE = os.path.join(settings.BASE_DIR, 'imagesservice/api/tests/data/images/random.txt')
IMAGE_TOO_SMALL = os.path.join(settings.BASE_DIR, 'imagesservice/api/tests/data/images/image_too_small.jpg')
