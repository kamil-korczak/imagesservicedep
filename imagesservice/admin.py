from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as UserAdminBase
from django.contrib.auth.models import User as DefaultUser
from django.http.request import HttpRequest
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (AccountTier, ThumbnailSize, UserAccountTier, Image, ThumbnailImage, ExpiringImage)


class UserInline(admin.TabularInline):
    model = UserAccountTier


class UserAdmin(UserAdminBase):
    inlines = (UserInline,)
    list_display = ("username", "email", "first_name", "last_name", "is_staff", "get_account_tier")

    @admin.display(description="Account tier")
    def get_account_tier(self, obj):
        return obj.useraccounttier.account_tier


admin.site.unregister(DefaultUser)
admin.site.register(DefaultUser, UserAdmin)


class ThumbnailSizeInline(admin.TabularInline):
    model = ThumbnailSize.tiers.through
    verbose_name = "Thumbnail size"
    extra = 1  # The number of empty forms to display
    template = "admin/templates/admin/edit_inline/tabular.html"


@admin.register(AccountTier)
class AccountTierAdmin(admin.ModelAdmin):
    inlines = (ThumbnailSizeInline, )
    list_display = ('__str__', 'is_builtin')
    exclude = ('is_builtin',)

    def has_change_permission(self, request, obj=None):
        if obj and obj.is_builtin:
            return False
        return super().has_change_permission(request, obj=obj)

    def has_delete_permission(self, request, obj=None):
        if obj and obj.is_builtin:
            return False
        return super().has_delete_permission(request, obj=obj)


@admin.register(ThumbnailSize)
class ThumbnailSizeAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'is_builtin')
    exclude = ('is_builtin',)

    def has_change_permission(self, request, obj=None):
        if obj and obj.is_builtin:
            return False
        return super().has_change_permission(request, obj=obj)

    def has_delete_permission(self, request, obj=None):
        if obj and obj.is_builtin:
            return False
        return super().has_delete_permission(request, obj=obj)


class ThumbnailImagesInline(admin.TabularInline):
    model = ThumbnailImage
    extra = 0
    readonly_fields = ('height', 'get_image_url', 'filename')

    def has_add_permission(self, *args) -> bool:
        return False

    @admin.display(description="Image url")
    def get_image_url(self, obj):
        link = obj.image_url
        return mark_safe(f'<a href="{link}">{link}</a>')


class ExpiringImagesInline(admin.TabularInline):
    model = ExpiringImage
    extra = 0
    fields = ('creation_datetime', 'expire_after', 'expiration_datetime', 'get_is_active', 'get_image_url')
    readonly_fields = ('creation_datetime', 'expiration_datetime', 'get_is_active', 'get_image_url')
    ordering = ('-expiration_datetime', )

    @admin.display(description="Is active")
    def get_is_active(self, obj):
        return not obj.is_expired

    @admin.display(description="Image url")
    def get_image_url(self, obj):
        link = obj.image_url
        return mark_safe(f'<a href="{link}">{link}</a>')

    get_is_active.boolean = True


@admin.register(Image)
class ImagesAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'image_tag', 'get_user_link')
    readonly_fields = ('image_tag', 'get_image_url', 'upload_datetime', 'update_datetime')
    inlines = (ThumbnailImagesInline, ExpiringImagesInline)
    ordering = ('-upload_datetime',)
    list_filter = ('user', )
    preserve_filters = ()

    fieldsets = (
        (None, {
            "fields": (
                "user", "image_tag", "get_image_url", "filename", "upload_datetime", "update_datetime"
            ),
        }),
    )

    @admin.display(description="User")
    def get_user_link(self, obj):
        link = reverse("admin:auth_user_change", args=[obj.user.id])
        return mark_safe(f'<a href="{link}">{obj.user}</a>')

    @admin.display(description="Image url")
    def get_image_url(self, obj):
        link = obj.image_url
        return mark_safe(f'<a href="{link}">{link}</a>')


# @admin.register(ThumbnailImage)
class ThumbnailImagesAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'height', 'image_tag', 'get_user_link')
    ordering = ('-image__upload_datetime',)
    list_filter = ('image__user', 'height')
    readonly_fields = ('image_tag', 'get_user_link',)

    fieldsets = (
        (None, {
            "fields": (
                ('image', 'height', 'image_tag', 'get_user_link',)
            ),
        }),
    )

    @admin.display(description="User")
    def get_user_link(self, obj):
        link = reverse("admin:auth_user_change", args=[obj.image.user.id])
        return mark_safe(f'<a href="{link}">{obj.image.user}</a>')

    def has_change_permission(self, request, obj=None) -> bool:
        return False


class AreNotExpiredFilter(admin.SimpleListFilter):
    title = "Expired"
    parameter_name = "expired"

    def lookups(self, request, model_admin):
        return (
            ('no', 'Active'),
            ('yes', 'Expired'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            qs_expired_images = ExpiringImage.objects.expired().values_list('id')
            return queryset.filter(id__in=qs_expired_images)
        elif self.value() == 'no':
            qs_not_expired_images = ExpiringImage.objects.active().values_list('id')
            return queryset.filter(id__in=qs_not_expired_images)


@admin.register(ExpiringImage)
class ExpiringImagesAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'image_tag', 'get_is_active', 'get_user_link')
    ordering = ('-expiration_datetime', '-creation_datetime',)
    list_filter = ('image__user', AreNotExpiredFilter)
    readonly_fields = ('image_tag', 'get_image_url', 'get_is_active', 'creation_datetime', 'expiration_datetime', 'get_user_link')
    fieldsets = (
        (None, {
            "fields": (
                ('image_tag', 'get_image_url', 'get_is_active', 'creation_datetime', 'expire_after', 'expiration_datetime', 'get_user_link')
            ),
        }),
    )

    @admin.display(description="Is active")
    def get_is_active(self, obj):
        return not obj.is_expired

    @admin.display(description="Image url")
    def get_image_url(self, obj):
        link = obj.image_url
        return mark_safe(f'<a href="{link}">{link}</a>')

    @admin.display(description="User")
    def get_user_link(self, obj):
        link = reverse("admin:auth_user_change", args=[obj.image.user.id])
        return mark_safe(f'<a href="{link}">{obj.image.user}</a>')

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    get_is_active.boolean = True
