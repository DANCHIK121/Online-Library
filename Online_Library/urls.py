from django.contrib import admin
from django.urls import path

from main import views

urlpatterns = [
    # Pages
    path("admin/", admin.site.urls),
    path("", views.home_page, name="home"),
    path("home/", views.home_page, name="home"),
    path("login_page/", views.login_page, name="login"),
    path("add_book_page/", views.add_book_page, name="add_book_page"),
    path("profile_page/", views.personal_account_page, name="profile"),
    path("registration_page/", views.register_page, name="registration"),
    path("personal_data_page/", views.personal_data_page, name="personal_data_page"),

    # Handlers
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.register, name='register'),
]
