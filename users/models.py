from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    """
    Кастомная модель пользователя, расширяющая стандартную.
    """
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Телефон"
    )

    phone_2 = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Второй телефон"
    )

    birthdate = models.DateField(
        blank=True,
        null=True,
        verbose_name="День рождения"
    )

    patronymic = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Отчество"
    )

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"