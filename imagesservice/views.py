
from django.http import HttpResponseNotFound, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from .config import UPGRADE_ACCOUNT_TIER_MESSAGE
from .models import Image, ExpiringImage, ThumbnailImage
from .utils import get_file_response


def serve_image(request, image_id):
    '''
    Serve original image
    '''
    image: Image = get_object_or_404(Image, id=image_id)
    if not image.can_be_displayed():
        return HttpResponseForbidden(UPGRADE_ACCOUNT_TIER_MESSAGE)
    return get_file_response(image.filename.path)


def serve_thumbnail_image(request, image_id):
    '''
    Serve original image
    '''
    image: ThumbnailImage = get_object_or_404(ThumbnailImage, id=image_id)
    if not image.can_be_displayed():
        return HttpResponseForbidden(UPGRADE_ACCOUNT_TIER_MESSAGE)
    return get_file_response(image.filename.path)


def serve_temp_image(request, image_id):
    '''
    Serve temporary, expiration image
    '''
    image: ExpiringImage = get_object_or_404(ExpiringImage, id=image_id)

    if not image.can_be_displayed():
        return HttpResponseForbidden(UPGRADE_ACCOUNT_TIER_MESSAGE)

    if image.is_expired:
        return HttpResponseNotFound("Image expired")

    return get_file_response(image.image.filename.path)
