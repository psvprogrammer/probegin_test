"""probegin_test URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls import url
from django.contrib.auth.views import login, logout
from django.contrib.staticfiles.urls import staticfiles_urlpatterns, static
from django.urls import path, re_path
from django.views.generic import TemplateView

from datetime import datetime

from probegin_test import views
from probegin_test.forms import CustomAuthenticationForm


urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', login,
        {
            'template_name': 'probegin_test/login.html',
            'authentication_form': CustomAuthenticationForm,
            'extra_context':
                {
                    'title': 'Login, please',
                    'year': datetime.now().year,
                }
        }, name='login'),
    path('logout/', logout,
        {
            'next_page': '/login'
        }, name='logout'),

    path('sign-up/', views.SignUp.as_view(), name='sign_up'),
    path('account_activation_sent/',
        TemplateView.as_view(template_name='probegin_test/account_activation_sent.html'),
        name='account_activation_sent'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),

    path('', TemplateView.as_view(template_name='probegin_test/home.html'),
         name='home'),

    path('blogs/', views.BlogList.as_view(), name='blog-list'),
    path('blogs/<int:author_id>/', views.AuthorBlogList.as_view(), name='author-blog-list'),
    path('my-blogs/', views.UserBlogList.as_view(), name='user-blog-list'),
    path('blog/details/<int:pk>/', views.BlogDetail.as_view(), name='blog-detail'),
    path('blog/add/', views.BlogCreate.as_view(), name='blog-add'),
    path('blog/<int:pk>/', views.BlogUpdate.as_view(), name='blog-update'),
    path('blog/<int:pk>/delete/', views.BlogDelete.as_view(), name='blog-delete'),
    path('blog-categories/', views.BlogCategories.as_view(), name='blog-categories-list'),
    path('blogs/category/<int:category_pk>/', views.BlogCategoryList.as_view(), name='category-blog-list'),

    path('my-posts/', views.UserPostList.as_view(), name='post-list'),
    path('blog/<int:blog_pk>/posts/', views.BlogPostList.as_view(), name='blog-post-list'),
    path('post/add/', views.PostCreate.as_view(), name='post-add'),
    path('post/<int:pk>/', views.PostUpdate.as_view(), name='post-update'),
    path('post/<int:pk>/delete/', views.PostDelete.as_view(), name='post-delete'),
    path('post/<int:post_pk>/comments/', views.PostCommentsList.as_view(), name='post-comments'),

    path('post/<int:post_pk>/comments/add/', views.CommentCreate.as_view(), name='comment-add'),
    path('add-comment/', views.CommentCreate.as_view(), name='ajax-comment-add'),
    path('post/<int:post_pk>/comments/<int:pk>/', views.CommentUpdate.as_view(), name='comment-update'),
    path('post/<int:post_pk>/comments/<int:pk>/delete/', views.CommentDelete.as_view(), name='comment-delete'),
]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)