from django.shortcuts import render

# Create your views here.
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.decorators import action, api_view

from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.viewsets import ModelViewSet

from product.models import Category, Product, Like, Comment
from product.permissions import IsAdminPermission, IsAuthorPermission
from product.serializers import CategorySerializer, ProductSerializer, ProductListSerializer, CommentSerializer


class CategoryListView(ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer




class ProductListView(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer



class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_url_kwarg = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['price', 'category']
    ordering_fields = ['created_at', 'price']
    search_fields = ['title', 'price', 'memory', 'storage', 'color']

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        return self.serializer_class



    @action(['POST'], detail=True)
    def comments(self, request, slug):
        product = self.get_object()
        comments = product.comments.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)


    @action(['POST'], detail=True)
    def like(self, request, slug=None):
        product = self.get_object()
        user = request.user
        try:
            like = Like.objects.get(product=product, user=user)
            like.is_liked = not like.is_liked
            like.save()
            message = 'liked' if like.is_liked else 'disliked'
        except Like.DoesNotExist:
            Like.objects.create(product=product, user=user, is_liked=True)
        return Response(message, status=200)


    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permissions = [IsAdminPermission]

        elif self.action == 'like':
            permissions = [IsAuthenticated]
        else:
            permissions = []
        return [perm() for perm in permissions]


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'products': reverse('product-list', request=request, format=format),
        'categories': reverse('categories-list', request=request, format=format),
    })

class CommentCreateView(CreateAPIView):
    queryset = Comment.objects.none()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, ]