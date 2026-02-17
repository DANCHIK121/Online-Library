from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    fieldsets = UserAdmin.fieldsets + (
        (('Дополнительная информация',), {'fields': ('phone', 'phone_2')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (('Дополнительная информация',), {'fields': ('phone', 'phone_2')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)