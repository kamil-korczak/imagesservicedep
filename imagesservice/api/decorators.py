from rest_framework.exceptions import ValidationError
from .utils import is_valid_uuid


def validate_image_id_format(image_id):
    if not is_valid_uuid(image_id):
        response_data = {'error': 'Invalid image_id format'}
        raise ValidationError(response_data)


def get_image_id_on_queryset(func):

    def wrapper(view_instance):
        image_id = view_instance.kwargs.get('image_id')
        validate_image_id_format(image_id)
        return func(view_instance, image_id)
    return wrapper
