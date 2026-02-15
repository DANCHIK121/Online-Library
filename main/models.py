from django.db import models
from django.contrib.auth.models import AbstractUser


class Profile(models.Model):
    email = models.CharField(max_length=40, null=False, default=""),
    username = models.CharField(max_length=40, null=False, default=""),
    password = models.CharField(max_length=15, null=False, default=""),
    first_name = models.CharField(max_length=40, null=False, default=""),
    last_name = models.CharField(max_length=40, null=False, default=""),
