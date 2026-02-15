from django.contrib import admin
from django.urls import path

from main import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', views.home_page, name="home"),
    path("registration/", views.register_page, name="registration"),
]
