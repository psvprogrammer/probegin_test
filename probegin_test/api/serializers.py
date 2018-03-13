from django.contrib.auth import get_user_model

from rest_framework import serializers
from rest_framework_jwt.settings import api_settings

from ..models import (
    BlogCategory,
    Blog,
    Post,
    Comment,
)


User = get_user_model()


class UserRegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password1 = serializers.CharField(default=None, style={'input_type': 'password'})
    password2 = serializers.CharField(default=None, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name',
                  'password1', 'password2')
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False},
        }


class UserActivationSerializer(serializers.Serializer):
    uid = serializers.CharField(required=True)
    token = serializers.CharField(required=True)

    class Meta:
        fields = ('uid', 'token')


class UserAuthSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(instance)
        token = jwt_encode_handler(payload)

        return {
            'id': instance.id,
            'username': instance.username,
            'token': token,
        }


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email')


class BlogCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogCategory
        fields = ('name',)


class BlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = ('author', 'title', 'description', 'categories')

    author = UserSerializer(read_only=True)
    categories = BlogCategorySerializer


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('author', 'blog', 'title', 'content')

    author = UserSerializer(read_only=True)
    blog = BlogSerializer


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('author', 'post', 'content')

    author = UserSerializer(read_only=True)
    post = PostSerializer
