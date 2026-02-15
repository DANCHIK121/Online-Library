from django.contrib import admin
from django.urls import path

from main import views

urlpatterns = [
    # Pages
    path('admin/', admin.site.urls),
    path('', views.home_page, name="home"),
    path('home/', views.home_page, name="home"),
    path("login_page/", views.login_page, name="login"),
    path("registration_page/", views.register_page, name="registration"),

    # Handlers
    path('register/', views.register, name='register'),
]
