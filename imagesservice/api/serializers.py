from django.utils import timezone
from rest_framework import serializers
from django.core.validators import MinValueValidator, MaxValueValidator
from rest_framework.validators import ValidationError
from django.conf import settings
from django.core.validators import FileExtensionValidator
from ..utils import validate_image_min_height
from ..models import ExpiringImage, Image, ThumbnailImage
from ..config import EXPIRE_AFTER_MIN, EXPIRE_AFTER_MAX

EXPIRING_IMAGES_EXPIRE_AFTER_VALIDATORS = [
    MinValueValidator(EXPIRE_AFTER_MIN),
    MaxValueValidator(EXPIRE_AFTER_MAX)
]


def get_host(instance):
    request = instance.context['request']
    is_request_secure = request.is_secure()
    protocol = 'https' if is_request_secure else 'http'
    host = instance.context['request'].get_host()
    return f"{protocol}://{host}"


class ExpiringImageListSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        data = data.filter(expiration_datetime__gt=timezone.now())
        return super().to_representation(data)


class ExpiringImageBaseSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(required=False, read_only=True)
    image_id = serializers.UUIDField(required=False, read_only=True)
    image_url = serializers.SerializerMethodField(read_only=True)
    expiration_datetime = serializers.DateTimeField(required=False, read_only=True)
    expire_after = serializers.IntegerField(required=False, validators=EXPIRING_IMAGES_EXPIRE_AFTER_VALIDATORS)

    class Meta:
        model = ExpiringImage
        fields = ['id', 'image_id', 'image_url', 'is_expired', 'creation_datetime', 'expiration_datetime', 'expire_after']

    def to_internal_value(self, data):
        copied_data = data.copy()
        action = self.context.get('action')
        if action and action == 'create':
            image_id = self.context.get('image_id')
            if image_id is not None:
                self.fields['image_id'] = serializers.UUIDField(required=True)
                copied_data['image_id'] = image_id
        return super(ExpiringImageBaseSerializer, self).to_internal_value(copied_data)

    def get_image_url(self, obj):
        return f"{get_host(self)}{obj.image_url}"

    def validate_image_id(self, image_id):
        user = self.context['request'].user
        try:
            data = Image.objects.get(user=user, id=image_id)
        except Image.DoesNotExist:
            raise ValidationError("Image doesn't exist")
        return data.id


class ExpiringImageCreateAndUpdateSerializer(ExpiringImageBaseSerializer):
    expire_after = serializers.IntegerField(required=True, validators=EXPIRING_IMAGES_EXPIRE_AFTER_VALIDATORS)


class ExpiringImagePutPatchSerializer(ExpiringImageBaseSerializer):
    expire_after = serializers.IntegerField(required=True, validators=EXPIRING_IMAGES_EXPIRE_AFTER_VALIDATORS)

    class Meta:
        model = ExpiringImage
        fields = ('expire_after', )


class ExpiringImageNestedSerializer(ExpiringImageBaseSerializer):

    class Meta:
        model = ExpiringImageBaseSerializer.Meta.model
        fields = ExpiringImageBaseSerializer.Meta.fields
        list_serializer_class = ExpiringImageListSerializer


class ThumbnailsImageListSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        user = self.context.get('request').user
        allowed_thumbnails_heights = []
        if hasattr(user, 'useraccounttier'):
            allowed_thumbnails_heights = user.useraccounttier.account_tier.allowed_thumbnails_heights
        data = data.filter(height__in=allowed_thumbnails_heights)
        return super().to_representation(data)


class ThumbnailImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ThumbnailImage
        list_serializer_class = ThumbnailsImageListSerializer
        fields = ('id', 'image_url', 'height', 'upload_datetime', 'update_datetime')

    def get_image_url(self, obj):
        return f"{get_host(self)}{obj.image_url}"


class ImageSerializer(serializers.ModelSerializer):
    filename = serializers.ImageField(required=False,
                                      validators=[
                                          FileExtensionValidator(allowed_extensions=settings.ALLOWED_IMAGE_EXTENSIONS),
                                          validate_image_min_height])
    image_url = serializers.SerializerMethodField(read_only=True)
    thumbnail_images = ThumbnailImageSerializer(read_only=True, many=True)
    expiring_images = ExpiringImageNestedSerializer(read_only=True, many=True, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user = kwargs['context']['request'].user
        user_has_account_tier = hasattr(user, 'useraccounttier')
        if user_has_account_tier and not user.useraccounttier.account_tier.can_see_expiring_img():
            self.fields.pop('expiring_images')

    class Meta:
        model = Image
        fields = ['id', 'filename', 'image_url', 'upload_datetime', 'update_datetime', 'thumbnail_images', 'expiring_images']

    def get_fields(self, *args, **kwargs):
        fields = super(ImageSerializer, self).get_fields(*args, **kwargs)
        request = self.context.get('request', None)
        if request and getattr(request, 'method', None) == "POST":
            fields['filename'].required = True
        return fields

    def get_image_url(self, obj):
        return f"{get_host(self)}{obj.image_url}"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        user = self.context['request'].user
        data.pop('filename')
        if hasattr(user, 'useraccounttier') and user.useraccounttier.account_tier.can_see_original_img():
            return data
        data.pop('image_url')
        return data
