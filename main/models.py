import uuid

from django.db import models
from django.urls import reverse

from users.models import CustomUser

class Genre(models.Model):
    name = models.CharField(max_length=200, help_text="Введите жанр книги (например, Научная фантастика)")

    def __str__(self):
        return self.name

class Language(models.Model):
    name = models.CharField(max_length=200, help_text="Введите язык книги (например, Английский, Русский)")

    def __str__(self):
        return self.name

class Author(models.Model):
    first_name = models.CharField(max_length=100, verbose_name="Имя")
    last_name = models.CharField(max_length=100, verbose_name="Фамилия")
    date_of_birth = models.DateField(null=True, blank=True, verbose_name="Дата рождения")
    date_of_death = models.DateField(null=True, blank=True, verbose_name="Дата смерти")

    class Meta:
        ordering = ["last_name", "first_name"]
        verbose_name = "Автор"
        verbose_name_plural = "Авторы"

    def get_absolute_url(self):
        return reverse('author-detail', args=[str(self.id)])

    def __str__(self):
        return f'{self.last_name}, {self.first_name}'

class Book(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название")
    author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True, verbose_name="Автор")
    summary = models.TextField(max_length=1000, help_text="Введите краткое описание книги", verbose_name="Аннотация")
    isbn = models.CharField('ISBN', max_length=13, unique=True, help_text='13-символьный <a href="https://www.isbn-international.org/content/what-isbn">номер ISBN</a>')
    genre = models.ManyToManyField(Genre, help_text="Выберите жанр для этой книги", verbose_name="Жанр")
    language = models.ForeignKey('Language', on_delete=models.SET_NULL, null=True, verbose_name="Язык")
    full_text = models.TextField(help_text="Полное содержание книги", verbose_name="Полный текст", blank=True)

    class Meta:
        verbose_name = "Книга"
        verbose_name_plural = "Книги"

    def display_genre(self):
        return ', '.join(genre.name for genre in self.genre.all()[:3])

    def get_absolute_url(self):
        return reverse('book-detail', args=[str(self.id)])

    def __str__(self):
        return self.title

class BookInstance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text="Уникальный ID для этой копии книги во всей библиотеке")
    book = models.ForeignKey('Book', on_delete=models.SET_NULL, null=True, verbose_name="Книга")
    imprint = models.CharField(max_length=200, verbose_name="Издание")
    due_back = models.DateField(null=True, blank=True, verbose_name="Дата возврата")
    borrower = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Арендатор")

    LOAN_STATUS = (
        ('m', 'На обслуживании'),
        ('o', 'Выдана'),
        ('a', 'Доступна'),
        ('r', 'Зарезервирована'),
    )

    status = models.CharField(
        max_length=1,
        choices=LOAN_STATUS,
        blank=True,
        default='m',
        help_text='Доступность книги',
        verbose_name="Статус"
    )

    class Meta:
        ordering = ["due_back"]
        permissions = (("can_mark_returned", "Set book as returned"),)
        verbose_name = "Экземпляр книги"
        verbose_name_plural = "Экземпляры книг"

    def __str__(self):
        return f'{self.id} ({self.book.title})'