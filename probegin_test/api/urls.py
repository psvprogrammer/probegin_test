from django.conf.urls import url
from rest_framework import routers
from . import views


router = routers.DefaultRouter()
router.register('register', views.RegisterAccountViewSet, base_name='register')
router.register('users', views.UserViewSet, base_name='users')
router.register('blog-categories', views.BlogCategoryViewSet, base_name='blogcategories')
router.register('blogs', views.BlogViewSet, base_name='blogs')
router.register('posts', views.PostViewSet, base_name='posts')
router.register('comments', views.CommentViewSet, base_name='comments')

urlpatterns = [
    url('activate-user', views.UserActivateView.as_view(), name='api-user-activate'),
]
