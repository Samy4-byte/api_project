from rest_framework import serializers

from product.models import Category, Product, Comment


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('title', 'image')

    def validate(self, title):
        if self.Meta.model.objects.filter(title=title).exists():
            raise serializers.ValidationError('Заголовок не может повторяться')
        return title



class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


    def get_fields(self):
        action = self.context.get('action')
        fields = super().get_fields()
        if action == 'create':
            fields.pop('slug')
        return fields

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['category'] = CategorySerializer(instance.category, context=self.context).data
        representation['comments'] = CommentSerializer(instance.comments.all(), many=True).data
        representation['likes'] = instance.likes.count()
        return representation

class ProductListSerializer(serializers.ModelSerializer):
    details = serializers.HyperlinkedIdentityField(view_name='product-detail', lookup_field='slug')

    class Meta:
        model = Product
        fields = ['title', 'slug', 'image', 'price', 'details']



class CommentSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = '__all__'

    def validate_rating(self, rating):
        if rating not in range(1, 11):
            raise serializers.ValidationError('Укажите рейтинг от 1 до 10')
        return rating

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        comment = Comment.objects.create(user=user, **validated_data)
        return comment
