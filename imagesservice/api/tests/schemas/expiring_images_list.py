from pytest_schema import schema, Or
from .expiring_image_details import EXPIRING_IMAGE_DETAILS_ENTERPRISE_SCHEMA


EXPIRING_IMAGES_LIST_ENTERPRISE_SCHEMA = schema(
    {
        "count": int,
        "next": Or(None, str),
        "previous": Or(None, str),
        "results": [
            EXPIRING_IMAGE_DETAILS_ENTERPRISE_SCHEMA
        ]
    }
)
