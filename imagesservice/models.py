import os
import uuid
from datetime import timedelta
from copy import copy
from typing import List
from PIL import Image as PIL_Image
from django.db import models
from django.utils import timezone
from django.utils.html import mark_safe
from django.contrib.auth.models import User as DefaultUser
from django.conf import settings
from django.core.cache import cache
from django.core.validators import FileExtensionValidator, MinValueValidator, MaxValueValidator
from .utils import GenerateRandomFileName, validate_image_min_height
from .config import EXPIRE_AFTER_MIN, EXPIRE_AFTER_MAX


class AccountTier(models.Model):
    name = models.CharField(verbose_name="Name", max_length=30, unique=True)

    # presence of the link to the originally uploaded file
    enable_original_link = models.BooleanField()

    # ability to generate expiring links
    enable_generate_expiring_links = models.BooleanField()

    is_builtin = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def can_see_original_img(self):
        return self.enable_original_link

    def can_see_expiring_img(self):
        return self.enable_generate_expiring_links

    @property
    def allowed_thumbnails_heights(self) -> List[int]:
        return list(self.thumbnailsize_set.values_list("height", flat=True))


class ThumbnailSizeManager(models.Manager):
    def get_max_height(self):
        max_height = cache.get('max_thumbnail_height')

        if max_height is None:
            max_height = self.aggregate(models.Max('height'))['height__max']
            cache.set('max_thumbnail_height', max_height, 3600)

        return max_height


class ThumbnailSize(models.Model):
    tiers = models.ManyToManyField(AccountTier, blank=True)
    height = models.IntegerField(verbose_name="height in px", unique=True)
    is_builtin = models.BooleanField(default=False)
    objects = ThumbnailSizeManager()

    def __str__(self):
        return f"{self.height} px in height"


class UserAccountTier(models.Model):
    account_tier = models.ForeignKey(AccountTier, on_delete=models.CASCADE)
    user = models.OneToOneField(DefaultUser, on_delete=models.CASCADE)


class Image(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    user = models.ForeignKey(DefaultUser, on_delete=models.CASCADE)
    upload_datetime = models.DateTimeField(auto_now_add=True)
    update_datetime = models.DateTimeField(auto_now=True)
    filename = models.ImageField(
        upload_to=GenerateRandomFileName("images/originals/"),
        validators=[FileExtensionValidator(allowed_extensions=settings.ALLOWED_IMAGE_EXTENSIONS), validate_image_min_height]
    )

    def __str__(self):
        return f"{self.id}"

    @property
    def image_url(self):
        return f"/img/{self.id}/"

    @property
    def image_tag(self):
        if thumbnail := self.thumbnail_images.all().order_by('height').first():
            image_tag_src = thumbnail.filename.url
        else:
            image_tag_src = self.filename.url
        return mark_safe(f'<img src="{image_tag_src}" height="55" />')

    def can_be_displayed(self):
        return self.user.useraccounttier.account_tier.can_see_original_img()

    def get_allowed_thumbnails_heights(self):
        return self.user.useraccounttier.account_tier.allowed_thumbnails_heights

    def create_thumbnails(self):
        original_image = PIL_Image.open(self.filename.path)
        original_height = original_image.height
        original_width = original_image.width

        for allowed_thumbnail_height in self.get_allowed_thumbnails_heights():
            image_to_thumbnail = copy(original_image)

            # calculate thumbnail size
            ratio = allowed_thumbnail_height / original_height
            new_width = int(original_width * ratio)
            thumbnail_size = (new_width, allowed_thumbnail_height)  # (max_width, max_height)

            image_to_thumbnail.thumbnail(thumbnail_size)

            # Create the directory if it doesn't exist
            thumbnail_dir = 'images/thumb/'
            os.makedirs(os.path.join(settings.MEDIA_ROOT, thumbnail_dir), exist_ok=True)
            thumbnail_image_path = GenerateRandomFileName(thumbnail_dir)(filename=self.filename.path)

            image_to_thumbnail.save(os.path.join(settings.MEDIA_ROOT, thumbnail_image_path))

            thumbnail_image, created = ThumbnailImage.objects.update_or_create(
                image=self,
                height=allowed_thumbnail_height,
                defaults={'filename': thumbnail_image_path}
            )

            thumbnail_image.save()

    def filename_has_changed(self):
        if self.pk:
            original_obj = Image.objects.filter(pk=self.pk).first()
            if original_obj and self.filename == original_obj.filename:
                return False
        return True

    def save(self, *args, **kwargs) -> None:
        if self.filename_has_changed():
            super().save(*args, **kwargs)
            self.create_thumbnails()
            return
        super().save(*args, **kwargs)


class ThumbnailImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    image = models.ForeignKey(Image, on_delete=models.CASCADE, related_name="thumbnail_images")
    height = models.IntegerField()
    upload_datetime = models.DateTimeField(auto_now_add=True)
    update_datetime = models.DateTimeField(auto_now=True)
    filename = models.ImageField(upload_to=GenerateRandomFileName("images/thumb/"))

    def __str__(self):
        return f"{self.id}"

    @property
    def image_tag(self):
        smallest_thumbnail = self.image.thumbnail_images.all().order_by('height').first()
        return mark_safe(f'<img src="{smallest_thumbnail.filename.url}" height="55" />')

    @property
    def image_url(self):
        return f"/img/thumb/{self.id}/"

    def can_be_displayed(self):
        return self.height in self.image.user.useraccounttier.account_tier.allowed_thumbnails_heights


class ExpiringImageManager(models.Manager):
    def active(self):
        return self.filter(expiration_datetime__gt=timezone.now())

    def expired(self):
        return self.filter(expiration_datetime__lt=timezone.now())


class ExpiringImage(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    image = models.ForeignKey(Image, on_delete=models.CASCADE, related_name="expiring_images")
    creation_datetime = models.DateTimeField(auto_now_add=True)
    expiration_datetime = models.DateTimeField()
    expire_after = models.IntegerField(
        help_text="Expire after given number of seconds",
        validators=[
            MinValueValidator(EXPIRE_AFTER_MIN, message=f"expire_after must be at least {EXPIRE_AFTER_MIN}"),
            MaxValueValidator(EXPIRE_AFTER_MAX, message=f"expire_after cannot exceed {EXPIRE_AFTER_MAX}")
        ]
        )
    objects = ExpiringImageManager()

    def __str__(self):
        return f"{self.id}"

    @property
    def is_expired(self):
        if self.expiration_datetime is None:
            return False
        check = timezone.now() > self.expiration_datetime
        return check

    @property
    def image_tag(self):
        if thumbnail := self.image.thumbnail_images.all().order_by('height').first():
            image_tag_src = thumbnail.filename.url
        else:
            image_tag_src = self.image.filename.url
        return mark_safe(f'<img src="{image_tag_src}" height="55" />')

    def can_be_displayed(self):
        return self.image.user.useraccounttier.account_tier.can_see_expiring_img()

    @property
    def image_url(self):
        return f"/img/temp/{self.id}/"

    def save(self, *args, **kwargs) -> None:
        time_delta = timedelta(seconds=self.expire_after)
        if self.creation_datetime:
            base_time = self.creation_datetime
        else:
            base_time = timezone.now()
        self.expiration_datetime = base_time + time_delta
        super().save(*args, **kwargs)
