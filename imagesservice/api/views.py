from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import BasePermission
from rest_framework.exceptions import NotFound
from rest_framework.filters import BaseFilterBackend
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from . import serializers
from ..models import ExpiringImage, Image
from .decorators import get_image_id_on_queryset


class Pagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 10


class ImageViewSet(ModelViewSet):
    serializer_class = serializers.ImageSerializer
    pagination_class = Pagination

    def get_queryset(self):
        queryset = Image.objects.filter(user=self.request.user).order_by('-upload_datetime')
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def options(self, request, *args, **kwargs):
        metadata = self.metadata_class()
        data = metadata.determine_metadata(request, view=self)
        return Response(data)


class ExpiringImageFilter(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        show = request.query_params.get('show')
        if show:
            if show == 'expired':
                return queryset.filter(expiration_datetime__lt=timezone.now())
            elif show == 'all':
                return queryset
        return queryset.filter(expiration_datetime__gt=timezone.now())


class ExpiringImagePermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if hasattr(user, 'useraccounttier'):
            return user.useraccounttier.account_tier.can_see_expiring_img()
        return False


class ExpiringImageViewSet(ModelViewSet):
    serializer_class = serializers.ExpiringImageBaseSerializer
    pagination_class = Pagination
    list_view_filter_backends = (ExpiringImageFilter, )
    permission_classes = (ExpiringImagePermission, )

    @get_image_id_on_queryset
    def get_queryset(self, image_id):
        try:
            Image.objects.get(id=image_id)
            queryset = ExpiringImage.objects.filter(image__id=image_id, image__user=self.request.user).order_by('-expiration_datetime', '-creation_datetime')
            if self.action == 'list':
                for filter_backend in self.list_view_filter_backends:
                    queryset = filter_backend().filter_queryset(self.request, queryset, view=self)
            return queryset
        except Image.DoesNotExist:
            raise NotFound("Image not found", code=status.HTTP_400_BAD_REQUEST)

    def options(self, request, *args, **kwargs):
        metadata = self.metadata_class()
        data = metadata.determine_metadata(request, view=self)
        data['optional_params'] = {
                'show': {
                    'type': 'string',
                    'default': 'active',
                    'options': ['active', 'expired', 'all'],
                    'description': 'An optional parameter for filtering expiring images.',
                }
            }
        return Response(data)

    def get_serializer_class(self):
        if self.action in ['create', ' update', 'partial_update']:
            return serializers.ExpiringImageCreateAndUpdateSerializer
        return super().get_serializer_class()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['action'] = self.action
        image_id = self.kwargs.get('image_id')
        if image_id:
            context['image_id'] = image_id
        return context

    def create(self, request, *args, **kwargs):
        raw_response = super().create(request, *args, **kwargs)
        data = raw_response.data
        response = {
            "id": data['id'],
            "image_url": data['image_url'],
            "expiration_datetime": data['expiration_datetime'],
            "expire_after": data['expire_after'],
        }
        return Response(response, status=status.HTTP_201_CREATED)
