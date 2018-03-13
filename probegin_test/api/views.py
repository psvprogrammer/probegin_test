from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_text, force_bytes

from rest_framework import viewsets, status, mixins
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import (
    BlogCategory, Blog,
    Post,
    Comment,
)

from .serializers import (
    UserRegisterSerializer,
    UserActivationSerializer,
    UserAuthSerializer,
    UserSerializer,
    BlogCategorySerializer,
    BlogSerializer,
    PostSerializer,
    CommentSerializer,
)

User = get_user_model()


class RegisterAccountViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    permission_classes = ()
    serializer_class = UserRegisterSerializer
    model = User

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.POST)
        form = UserCreationForm(request.POST)
        if form.is_valid():
            if serializer.is_valid():
                user = form.save(commit=False)
                user.email = serializer.validated_data.get('email')
                user.is_active = False
                user.save()
                data = {
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': default_token_generator.make_token(user),
                    'user': UserSerializer(user).data,
                }
                return Response(data=data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors,
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(data=form.errors,
                            status=status.HTTP_400_BAD_REQUEST)


class UserActivateView(APIView):
    permission_classes = []
    queryset = User.objects.all()
    serializer_class = UserActivationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.POST)
        if serializer.is_valid():
            uid = force_text(urlsafe_base64_decode(
                serializer.validated_data.get('uid')))
            try:
                user = User.objects.get(pk=uid)
            except User.DoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST)

            if default_token_generator.check_token(
                    user, serializer.validated_data.get('token')):
                user.is_active = True
                user.profile.email_confirmed = True
                user.save()
                return Response(data=UserAuthSerializer(user).data,
                                status=status.HTTP_200_OK)
            else:
                return Response(data={'error': 'Invalid token or user id!'},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class BlogCategoryViewSet(viewsets.ModelViewSet):
    queryset = BlogCategory.objects.all()
    serializer_class = BlogCategorySerializer


class BlogViewSet(viewsets.ModelViewSet):
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
