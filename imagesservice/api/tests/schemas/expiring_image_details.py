from pytest_schema import schema, Regex
from .config import SCHEMA_ID_REGEX, SCHEMA_DATETIME_REGEX, UUID4_REGEX


EXPIRING_IMAGE_DETAILS_ENTERPRISE_SCHEMA = schema(
    {
        "id": SCHEMA_ID_REGEX,
        "image_id": SCHEMA_ID_REGEX,
        "image_url": Regex(rf'https?://(.*)/img/temp/{UUID4_REGEX}/'),
        "is_expired": bool,
        "creation_datetime": SCHEMA_DATETIME_REGEX,
        "expiration_datetime": SCHEMA_DATETIME_REGEX,
        "expire_after": lambda expire_after: expire_after in range(300, 30001)
    }
)
