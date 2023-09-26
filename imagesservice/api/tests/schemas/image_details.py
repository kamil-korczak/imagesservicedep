from pytest_schema import schema, And
from ..config import BASIC_ALLOWED_THUMBNAIL_HEIGHTS, PREMIUM_ALLOWED_THUMBNAIL_HEIGHTS, ENTERPRISE_ALLOWED_THUMBNAIL_HEIGHTS
from .config import SCHEMA_ID_REGEX, SCHEMA_DATETIME_REGEX, SCHEMA_IMG_URL_REGEX, SCHEMA_THUMB_URL_REGEX
from .expiring_image_details import EXPIRING_IMAGE_DETAILS_ENTERPRISE_SCHEMA


IMAGE_DETAILS_BASIC_SCHEMA = schema(
    {
        "id": SCHEMA_ID_REGEX,
        "upload_datetime": SCHEMA_DATETIME_REGEX,
        "update_datetime": SCHEMA_DATETIME_REGEX,
        "thumbnail_images": And([
            {
                "id": SCHEMA_ID_REGEX,
                "image_url": SCHEMA_THUMB_URL_REGEX,
                "height": And(int, lambda height: height in BASIC_ALLOWED_THUMBNAIL_HEIGHTS),
                "upload_datetime": SCHEMA_DATETIME_REGEX,
                "update_datetime": SCHEMA_DATETIME_REGEX
            }
        ], lambda item: len(item) == 1)
    }
)


IMAGE_DETAILS_PREMIUM_SCHEMA = schema(
    {
        "id": SCHEMA_ID_REGEX,
        "image_url": SCHEMA_IMG_URL_REGEX,
        "upload_datetime": SCHEMA_DATETIME_REGEX,
        "update_datetime": SCHEMA_DATETIME_REGEX,
        "thumbnail_images": And([
            {
                "id": SCHEMA_ID_REGEX,
                "image_url": SCHEMA_THUMB_URL_REGEX,
                "height": And(int, lambda height: height in PREMIUM_ALLOWED_THUMBNAIL_HEIGHTS),
                "upload_datetime": SCHEMA_DATETIME_REGEX,
                "update_datetime": SCHEMA_DATETIME_REGEX
            }
        ], lambda item: len(item) == 2)
    }
)


IMAGE_DETAILS_ENTERPRISE_SCHEMA = schema(
    {
        "id": SCHEMA_ID_REGEX,
        "image_url": SCHEMA_IMG_URL_REGEX,
        "upload_datetime": SCHEMA_DATETIME_REGEX,
        "update_datetime": SCHEMA_DATETIME_REGEX,
        "thumbnail_images": And([
            {
                "id": SCHEMA_ID_REGEX,
                "image_url": SCHEMA_THUMB_URL_REGEX,
                "height": And(int, lambda height: height in ENTERPRISE_ALLOWED_THUMBNAIL_HEIGHTS),
                "upload_datetime": SCHEMA_DATETIME_REGEX,
                "update_datetime": SCHEMA_DATETIME_REGEX
            }
        ], lambda item: len(item) == 2),
        "expiring_images": [EXPIRING_IMAGE_DETAILS_ENTERPRISE_SCHEMA]
    }
)
