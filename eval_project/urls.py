"""eval_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Import the include() function: from django.conf.urls import url, include
    3. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from django.views.generic import TemplateView
from django.contrib.auth.views import login, logout

from map_app import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^address$', views.address_view, name='address'),
    url(r'^reset-address$', views.reset_address, name='reset-address'),
    url(r'^fusion-tables$', views.FusionTableHandler.as_view(), name='fusion-tables'),
    url(r'^oauth2callback$', views.oauth_callback, name='oauth2-callback'),
    url(r'^accounts/login/$', login, {'template_name': 'admin/login.html'}, name='login'),
    url(r'^accounts/logout/$', logout, {'next_page': '/'}, name='logout'),
    url(r'^admin/', admin.site.urls),
] + static(settings.STATIC_URL,
           document_root=settings.STATIC_ROOT)
