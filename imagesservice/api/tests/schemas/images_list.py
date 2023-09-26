from pytest_schema import schema, Or
from .image_details import IMAGE_DETAILS_BASIC_SCHEMA, IMAGE_DETAILS_PREMIUM_SCHEMA, IMAGE_DETAILS_ENTERPRISE_SCHEMA


IMAGES_LIST_BASIC_SCHEMA = schema(
    {
        "count": int,
        "next": Or(None, str),
        "previous": Or(None, str),
        "results": [
            IMAGE_DETAILS_BASIC_SCHEMA
        ]
    }
)

IMAGES_LIST_PREMIUM_SCHEMA = schema(
    {
        "count": int,
        "next": Or(None, str),
        "previous": Or(None, str),
        "results": [
            IMAGE_DETAILS_PREMIUM_SCHEMA
        ]
    }
)

IMAGES_LIST_ENTERPRISE_SCHEMA = schema(
    {
        "count": int,
        "next": Or(None, str),
        "previous": Or(None, str),
        "results": [
            IMAGE_DETAILS_ENTERPRISE_SCHEMA
        ]
    }
)
