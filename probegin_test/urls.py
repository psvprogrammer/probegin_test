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
from django.urls import path

from datetime import datetime

from probegin_test.forms import CustomAuthenticationForm

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^login$', login,
        {
            'template_name': 'probegin_test/login.html',
            'authentication_form': CustomAuthenticationForm,
            'extra_context':
                {
                    'title': 'Login, please',
                    'year': datetime.now().year,
                }
        }, name='login'),
    url(r'^logout$', logout,
        {
            'next_page': '/login'
        }, name='logout'),
]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)