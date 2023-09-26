import os
import uuid
from typing import Union
from PIL import Image
from django.http import FileResponse, HttpResponseNotFound
from django.utils.deconstruct import deconstructible
from django.core.exceptions import ValidationError
from django.apps import apps


def get_file_response(filename_path: str) -> Union[FileResponse, HttpResponseNotFound]:
    try:
        img_file = open(filename_path, 'rb')
        response = FileResponse(img_file)
    except FileNotFoundError:
        response = HttpResponseNotFound("Image not found")
    return response


@deconstructible
class GenerateRandomFileName(object):

    def __init__(self, path_prefix="media/"):
        self.path_prefix = path_prefix

    def __call__(self, instance=None, filename=''):
        ext = filename.split('.')[-1]
        random_filename = f"{uuid.uuid4().hex}.{ext}"
        return os.path.join(self.path_prefix, random_filename)


def validate_image_min_height(image):
    image_min_height = apps.get_model('imagesservice.ThumbnailSize').objects.get_max_height()
    with Image.open(image) as img:
        image_width, image_height = img.size
        if image_height < image_min_height:
            raise ValidationError(f"Image height must be at least {image_min_height} px, current have {image_height} px.")
