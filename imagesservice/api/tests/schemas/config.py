
from pytest_schema import Regex

UUID4_REGEX = '[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}'
SCHEMA_THUMB_URL_REGEX = Regex(rf'https?://(.*)/img/thumb/{UUID4_REGEX}/')
SCHEMA_IMG_URL_REGEX = Regex(rf'https?://(.*)/img/{UUID4_REGEX}/')
SCHEMA_ID_REGEX = Regex(rf"{UUID4_REGEX}")
SCHEMA_DATETIME_REGEX = Regex(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}Z')
