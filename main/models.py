from django.db import models
from django.contrib.auth.models import AbstractUser


class Profile(models.Model):
    email = models.CharField(max_length=40, null=False, default=""),
    username = models.CharField(max_length=40, null=False, default=""),
    password = models.CharField(max_length=15, null=False, default=""),
    first_name = models.CharField(max_length=40, null=False, default=""),
    last_name = models.CharField(max_length=40, null=False, default=""),


class CustomUser(AbstractUser):
    phone = models.CharField(max_length=15, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='customuser_set',
        related_query_name='customuser',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='customuser_set',
        related_query_name='customuser',
    )
