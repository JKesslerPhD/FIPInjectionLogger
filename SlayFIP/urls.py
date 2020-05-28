"""SlayFIP URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.urls import path
from InjectionLog import views
from django.contrib.auth import views as auth_views
from django.urls import include, path
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('log/', views.injectionlog),
    path('', views.main_site),
    path('information/',views.information),
    path('calculate/',views.calculatedosage),
    path('inject/',views.recordinjection),
    path('add_gs/', views.add_gs),
    path('catinfo/', views.catinfo),
    path('logout/',views.logout_view),
    path("register/", views.register, name="register"),
    path("delete/", views.delete_injection),
    path("make_test/", views.make_test),
    path('accounts/', include('django.contrib.auth.urls')),
]
