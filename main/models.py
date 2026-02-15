from django.db import models

class Users(models.Model):
    age = models.IntegerField(null=False)
    mail = models.CharField(max_length=40, null=False, default="")
    name = models.CharField(max_length=40, null=False, default="")
    phone_number = models.CharField(max_length=20, null=False, default="")
    second_phone_number = models.CharField(max_length=20, null=False, default="")
    passport_data = models.CharField(max_length=15, null=False, default="")
