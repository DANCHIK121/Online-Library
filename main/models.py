from django.db import models
from django.utils import timezone


class Book(models.Model):
    # Статусы наличия книги
    STATUS_CHOICES = [
        ('available', 'В наличии'),
        ('limited', 'Ограниченное количество'),
        ('out', 'Нет в наличии'),
        ('expected', 'Ожидается'),
    ]

    # Жанры книг
    GENRE_CHOICES = {
        'fiction': 'Художественная литература',
        'nonfiction': 'Нон-фикшн',
        'science': 'Научная литература',
        'fantasy': 'Фэнтези',
        'detective': 'Детектив',
        'romance': 'Роман',
        'poetry': 'Поэзия',
        'children': 'Детская литература',
        'history': 'История',
        'biography': 'Биография',
        'other': 'Другое',
    }

    # Языки
    LANGUAGE_CHOICES = [
        ('ru', 'Русский'),
        ('en', 'Английский'),
        ('de', 'Немецкий'),
        ('fr', 'Французский'),
        ('es', 'Испанский'),
        ('other', 'Другой'),
    ]

    # Основные поля
    title = models.CharField('Название', max_length=300)
    author = models.CharField('Автор', max_length=200, default='')
    year = models.IntegerField('Год издания', null=True, blank=True)
    isbn = models.CharField('ISBN', max_length=20, blank=True, null=True)
    publisher = models.CharField('Издательство', max_length=200, blank=True, null=True)
    pages = models.IntegerField('Количество страниц', blank=True, null=True)

    # Описание
    genre = models.CharField('Жанр', max_length=50, choices=GENRE_CHOICES, default='')
    description = models.TextField('Краткое описание', max_length=500, blank=True)
    full_description = models.TextField('Полное описание', blank=True)

    # Медиа-файлы
    cover_image = models.ImageField('Обложка', upload_to='static/covers/', blank=True, null=True)
    book_content = models.FileField('Текстовое содержание книги', upload_to='static/contents/', blank=True, null=True)
    book_file = models.FileField('Файл книги', upload_to='static/books/', blank=True, null=True)

    # Статус и количество
    quantity = models.IntegerField('Количество экземпляров', default=1)
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='available')
    language = models.CharField('Язык', max_length=20, choices=LANGUAGE_CHOICES, default='ru')

    # Дополнительные параметры (флаги)
    is_new = models.BooleanField('Новинка', default=False)
    is_bestseller = models.BooleanField('Бестселлер', default=False)
    is_recommended = models.BooleanField('Рекомендуемое', default=False)
    for_kids = models.BooleanField('Детская литература', default=False)
    limited_edition = models.BooleanField('Лимитированное издание', default=False)

    # Даты
    added_date = models.DateField('Дата добавления', default=timezone.now)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True, null=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Книга'
        verbose_name_plural = 'Книги'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.author}"

    def save(self, *args, **kwargs):
        if int(self.quantity) <= 0:
            self.status = 'out'
        elif int(self.quantity) < 3 and self.status != 'out':
            self.status = 'limited'
        super().save(*args, **kwargs)