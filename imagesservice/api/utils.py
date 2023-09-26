import uuid


def is_valid_uuid(uuid_str):
    try:
        uuid_obj = uuid.UUID(uuid_str)
        return uuid_obj.version == 4
    except ValueError:
        return False
