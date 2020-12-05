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
from django.urls import include, path, re_path
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('log/', views.injectionlog),
    path('', views.main_site),
    re_path('(.*?)service-worker.js', (TemplateView.as_view(
    template_name="InjectionLog/service-worker.js",
    content_type='application/javascript',
)), name='service-worker.js'),


    path('information/',views.information),
    path('calculate/',views.calculatedosage),
    path('inject/',views.recordinjection),
    path('add_gs/', views.add_gs),
    path('catinfo/', views.catinfo),
    path('bloodwork/', views.catinfo),
    path('logout/',views.logout_view),
    path("register/", views.register, name="register"),
    path("delete/", views.delete_injection),
    path("make_test/", views.make_test),
    path("record_observation/", views.record_observation),
    path("observationlog/", views.observation_log),
    path("upload_cbc/",views.upload_file),
    path("trackwarrior/",views.track_warrior),
    path("change_record/",views.change_record),
    path("costs/",views.costs),
    path("vetinfo/",views.vet_info),
    path("data/",views.data_analysis),
    path("brands/",views.brands),
    path('accounts/', include('django.contrib.auth.urls')),
    path("fix_timezone_error",views.fix_timezone),
    path("about/",views.about),
    path("error_create/",views.error_create),
]
