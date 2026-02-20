import re
import datetime

from .models import Book

from django.contrib import messages
from django.contrib.auth import logout
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required

User = get_user_model()

# Render pages
def home_page(request):
    books = Book.objects.all()

    context = {
        "books": books,
    }

    return render(request, "MainPage.html", context)

def register_page(request):
    return render(request, "RegisterPage.html")

def login_page(request):
    return render(request, "LoginPage.html")

@login_required(login_url='/login_page/')
def personal_account_page(request):
    user = request.user
    request.session['last_visit'] = str(datetime.datetime.now()).split(".")[0]
    return render(request, 'PersonalAccountPage.html', {'user': user})

def personal_data_page(request):
    return render(request, 'PersonalDataPage.html')

def add_book_page(request):
    return render(request, "AddBookPage.html")

@login_required(login_url='/login_page/')
def my_books_page(request):
    return render(request, "MyBooksPage.html")

def admin_page(request):
    total_books = Book.objects.count()

    # Другие данные для статистики
    active_readers = 342  # Это вы можете заменить на реальные данные из модели Reader
    books_issued = 127  # Замените на реальные данные из модели IssuedBook
    popular_books_count = Book.objects.filter(is_bestseller=True).count()  # Замените на реальные данные

    context = {
        'total_books': total_books,
        'active_readers': active_readers,
        'books_issued': books_issued,
        'popular_books_count': popular_books_count,
        'popular_books': [
            {'title': 'Война и мир', 'author': 'Толстой Л.Н.', 'issues': 23},
            {'title': 'Преступление и наказание', 'author': 'Достоевский Ф.М.', 'issues': 19},
            {'title': 'Мастер и Маргарита', 'author': 'Булгаков М.А.', 'issues': 17},
        ],
        'overdue_books': [
            {'reader': 'Иванов И.И.', 'book': 'Преступление и наказание', 'days': 5},
            {'reader': 'Петрова А.С.', 'book': 'Анна Каренина', 'days': 2},
            {'reader': 'Сидоров В.П.', 'book': 'Тихий Дон', 'days': 1},
        ]
    }

    return render(request, 'AdminPage.html', context)

@login_required(login_url='/login_page/')
def live_book_page(request):
    needed_book = Book.objects.get(title="Преступление и наказание")

    pdf_url = None
    if needed_book.book_file and hasattr(needed_book.book_file, 'url'):
        pdf_url = needed_book.book_file.url

    context = {
        "title":needed_book.title,
        "author":needed_book.author,
        "year":needed_book.year,
        "pages":needed_book.pages,
        "genre":Book.GENRE_CHOICES[needed_book.genre],
        "pdf_url":pdf_url,
    }

    return render(request, 'LiveBookPage.html', context)



# Handlers for pages work
def user_logout(request):
    logout(request)
    request.session.flush()
    return redirect('home')

@csrf_protect
def register(request):
    """Обработка регистрации нового пользователя"""
    if request.method == 'POST':
        # Getting data from the form
        lastname = request.POST.get('lastname')
        firstname = request.POST.get('firstname')
        patronymic = request.POST.get('patronymic')
        birthdate = request.POST.get('birthdate')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        alternate_phone = request.POST.get('alternate_phone', '')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        newsletter = request.POST.get('newsletter') == 'on'
        agreement = request.POST.get('agreement') == 'on'

        # Data validation
        errors = []

        # Checking required fields
        if not all([lastname, firstname, birthdate, email, phone, password, confirm_password]):
            errors.append("Все обязательные поля должны быть заполнены")

        # Verification of compliance with the rules
        if not agreement:
            errors.append("Необходимо согласие с правилами пользования библиотекой")

        # Password verification
        if password != confirm_password:
            errors.append("Пароли не совпадают")
        elif len(password) < 8:
            errors.append("Пароль должен содержать минимум 8 символов")

        # Checking email (to see if it is busy)
        if User.objects.filter(email=email).exists():
            errors.append("Пользователь с таким email уже зарегистрирован")

        # Phone verification (you can add your own logic)
        phone_pattern = r'^\+7 \(\d{3}\) \d{3}-\d{2}-\d{2}$'
        if not re.match(phone_pattern, phone):
            errors.append("Введите телефон в формате +7 (999) 123-45-67")

        if errors:
            # If there are errors, we show them to the user
            for error in errors:
                messages.error(request, error)
            return render(request, 'RegisterPage.html', {'form_data': request.POST})

        try:
            # Creating a user
            username = email  # We use email as username
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=firstname,
                last_name=lastname,
                phone=phone,
                phone_2=alternate_phone,
                birthdate=birthdate,
                patronymic=patronymic,
            )

            # Дополнительная информация о пользователе (если есть модель Profile)
            # profile = Profile.objects.create(
            #     user=user,
            #     patronymic=patronymic,
            #     birthdate=birthdate,
            #     phone=phone,
            #     alternate_phone=alternate_phone,
            #     address=address,
            #     newsletter=newsletter
            # )

            # Sending a welcome letter
            send_welcome_email(email, firstname)

            # Automatic login after registration
            login(request, user)

            # Success Message
            messages.success(request, f'Добро пожаловать, {firstname}! Регистрация прошла успешно.')

            # Redirection to the reader's ticket page or the main page
            return redirect('profile')

        except Exception as e:
            messages.error(request, f'Ошибка при регистрации: {str(e)}')
            return render(request, 'RegisterPage.html', {'form_data': request.POST})

    return render(request, 'RegisterPage.html')

@csrf_protect
def user_login(request):
    """Обработка входа пользователя"""
    if request.method == 'POST':
        # Getting data from the form
        email = request.POST.get('email')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me') == 'on'

        # Data validation
        errors = []

        # Checking required fields
        if not all([email, password]):
            errors.append("Все обязательные поля должны быть заполнены")

        # Password verification
        if len(password) < 8:
            errors.append("Пароль не может содержать миньше 8 символов")

        # Checking email (to see if it is busy)
        if not User.objects.filter(email=email).exists():
            errors.append("Пользователь с таким email не найден")

        if errors:
            # If there are errors, we show them to the user
            for error in errors:
                messages.error(request, error)
            return render(request, 'LoginPage.html', {'form_data': request.POST})

        try:
            try:
                user = User.objects.get(email=email)

                # Authentication
                authenticated_user = authenticate(request, username=user.username, password=password)

                if authenticated_user is not None:
                    # User login
                    login(request, authenticated_user)

                    # Setting up a session
                    if not remember_me:
                        request.session.set_expiry(1209600)  # The session expires when the browser is closed
                    else:
                        request.session.set_expiry(0)

                    messages.success(request, f'Добро пожаловать, {authenticated_user.username}!')

                    # Go to profile
                    return redirect('profile')
                else:
                    messages.error(request, 'Неверный пароль')

            except User.DoesNotExist:
                messages.error(request, 'Пользователь с таким email не найден')

        except Exception as e:
            messages.error(request, f'Ошибка при авторизации: {str(e)}')

        return render(request, 'LoginPage.html', {'form_data': request.POST})

    return render(request, 'LoginPage.html')

# def send_welcome_email(email, firstname):
#     """Отправка приветственного письма"""
#     subject = 'Добро пожаловать в Онлайн библиотеку!'
#     message = f'''
#     Здравствуйте, {firstname}!
#
#     Благодарим вас за регистрацию в нашей онлайн библиотеке.
#
#     Ваш электронный читательский билет доступен в личном кабинете.
#
#     С уважением,
#     Команда Онлайн библиотеки
#     '''
#     from_email = 'daniil_projects@mail.ru'
#     recipient_list = [email]
#
#     try:
#         send_mail(subject, message, from_email, recipient_list)
#     except:
#         pass

@csrf_protect
@login_required(login_url='/login_page/')
def add_book(request):
    """Обработка добавления новой книги в базу данных"""
    if request.method == 'POST':
        # Получаем данные из формы
        title = request.POST.get('title')
        author = request.POST.get('author')
        year = request.POST.get('year')
        isbn = request.POST.get('isbn', '')
        publisher = request.POST.get('publisher', '')
        pages = request.POST.get('pages')
        genre = request.POST.get('genre')
        description = request.POST.get('description', '')
        full_description = request.POST.get('full_description', '')
        quantity = request.POST.get('quantity', 1)
        status = request.POST.get('status', 'available')
        language = request.POST.get('language', 'ru')
        added_date = request.POST.get('added_date', datetime.date.today())

        cover_image = request.FILES.get('cover_image')
        book_content = request.FILES.get('book_content')
        book_file = request.FILES.get('book_file')

        is_new = request.POST.get('is_new') == 'yes'
        is_bestseller = request.POST.get('is_bestseller') == 'yes'
        is_recommended = request.POST.get('is_recommended') == 'yes'
        for_kids = request.POST.get('for_kids') == 'yes'
        limited_edition = request.POST.get('limited_edition') == 'yes'

        errors = []

        if not all([title, author, year, genre]):
            errors.append("Заполните все обязательные поля (название, автор, год, жанр)")

        if year:
            try:
                year_int = int(year)
                if year_int < 1000 or year_int > 2100:
                    errors.append("Год должен быть между 1000 и 2100")
            except ValueError:
                errors.append("Год должен быть числом")

        if pages:
            try:
                pages_int = int(pages)
                if pages_int < 1:
                    errors.append("Количество страниц должно быть положительным числом")
            except ValueError:
                errors.append("Количество страниц должно быть числом")

        if quantity:
            try:
                quantity_int = int(quantity)
                if quantity_int < 0:
                    errors.append("Количество экземпляров не может быть отрицательным")
            except ValueError:
                errors.append("Количество экземпляров должно быть числом")

        if isbn and len(isbn) > 20:
            errors.append("ISBN не может быть длиннее 20 символов")

        if isbn and Book.objects.filter(isbn=isbn).exists():
            errors.append("Книга с таким ISBN уже существует")

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'AddBookPage.html', {'form_data': request.POST})

        try:
            book = Book.objects.create(
                title=title,
                author=author,
                year=year,
                isbn=isbn if isbn else None,
                publisher=publisher if publisher else None,
                pages=pages if pages else None,
                genre=genre,
                description=description,
                full_description=full_description,
                quantity=quantity,
                status=status,
                language=language,
                added_date=added_date,
                cover_image=cover_image,
                book_file=book_file,
                book_content=book_content,
                is_new=is_new,
                is_bestseller=is_bestseller,
                is_recommended=is_recommended,
                for_kids=for_kids,
                limited_edition=limited_edition
            )

            messages.success(request, f'Книга "{title}" успешно добавлена в библиотеку!')

            return redirect('book_list')

        except Exception as e:
            messages.error(request, f'Ошибка при добавлении книги: {str(e)}')
            return render(request, 'AddBookPage.html', {'form_data': request.POST})

    return render(request, 'AddBookPage.html')

def send_welcome_email(email, firstname):
    """Отправка приветственного письма с HTML оформлением"""
    subject = '📚 Добро пожаловать в Онлайн библиотеку!'

    # Контекст для шаблона
    context = {
        'firstname': firstname,
        'login_url': 'https://online-library-for-yarik-from-daniil.cloudpub.ru/login_page/',
        'support_email': 'online_library_mail_box@mail.ru'
    }

    # HTML версия письма
    html_message = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f4f4f4;">
        <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f4f4f4;">
            <tr>
                <td align="center" style="padding: 40px 0;">
                    <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <!-- Шапка -->
                        <tr>
                            <td style="padding: 40px 40px 20px 40px; text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 8px 8px 0 0;">
                                <h1 style="color: #ffffff; margin: 0; font-size: 32px; font-weight: 300;">📖 Онлайн библиотека</h1>
                            </td>
                        </tr>

                        <!-- Основной контент -->
                        <tr>
                            <td style="padding: 40px;">
                                <h2 style="color: #333333; margin: 0 0 20px 0; font-size: 24px;">Здравствуйте, {firstname}!</h2>

                                <p style="color: #666666; line-height: 1.6; margin: 0 0 20px 0; font-size: 16px;">
                                    Благодарим вас за регистрацию в нашей онлайн библиотеке! 
                                    Мы рады приветствовать вас в сообществе любителей чтения.
                                </p>

                                <table width="100%" cellpadding="0" cellspacing="0" style="margin: 30px 0;">
                                    <tr>
                                        <td style="background-color: #f8f9fa; padding: 20px; border-radius: 6px;">
                                            <p style="color: #333333; margin: 0 0 10px 0; font-size: 18px; font-weight: bold;">
                                                ✅ Ваш электронный читательский билет
                                            </p>
                                            <p style="color: #666666; margin: 0; font-size: 14px;">
                                                Теперь вы можете пользоваться всеми возможностями библиотеки:<br>
                                                • Доступ к 10 000+ книг<br>
                                                • Сохранение закладок<br>
                                                • Синхронизация между устройствами<br>
                                                • Персональные рекомендации
                                            </p>
                                        </td>
                                    </tr>
                                </table>

                                <!-- Кнопки действий -->
                                <table width="100%" cellpadding="0" cellspacing="0">
                                    <tr>
                                        <td align="center" style="padding: 10px 0;">
                                            <a href="{context["login_url"]}" style="background-color: #764ba2; color: #ffffff; padding: 12px 30px; text-decoration: none; border-radius: 4px; display: inline-block; margin: 0 10px 10px 0; font-weight: bold;">🔑 Войти в личный кабинет</a>
                                        </td>
                                    </tr>
                                </table>

                                <hr style="border: none; border-top: 1px solid #eeeeee; margin: 30px 0;">

                                <p style="color: #999999; font-size: 14px; line-height: 1.6; margin: 0;">
                                    Если у вас возникли вопросы, напишите нам: 
                                    <a href="mailto:{context["support_email"]}" style="color: #667eea; text-decoration: none;">{context["support_email"]}</a>
                                </p>
                            </td>
                        </tr>

                        <!-- Подвал -->
                        <tr>
                            <td style="padding: 30px 40px; background-color: #f8f9fa; border-radius: 0 0 8px 8px;">
                                <p style="color: #999999; font-size: 14px; line-height: 1.6; margin: 0; text-align: center;">
                                    С уважением,<br>
                                    <strong style="color: #666666;">Команда Онлайн библиотеки</strong>
                                </p>
                                <p style="color: #cccccc; font-size: 12px; text-align: center; margin: 20px 0 0 0;">
                                    © 2026 Онлайн библиотека. Все права защищены.<br>
                                    Вы получили это письмо, потому что зарегистрировались на нашем сайте.
                                </p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    '''

    # Текстовая версия для спам-фильтров
    text_message = f'''
Здравствуйте, {firstname}!

Благодарим вас за регистрацию в нашей онлайн библиотеке!

✅ Ваш электронный читательский билет активирован
Теперь вам доступно:
- Более 10 000 книг
- Сохранение закладок
- Синхронизация между устройствами
- Персональные рекомендации

🔑 Войти в личный кабинет: {context["login_url"]}

Если у вас возникли вопросы: {context["support_email"]}

С уважением,
Команда Онлайн библиотеки
    '''

    from_email = 'daniil_projects@mail.ru'
    recipient_list = [email]

    try:
        # Отправляем HTML-письмо с текстовой альтернативой
        send_mail(
            subject=subject,
            message=text_message,  # текстовая версия
            from_email=from_email,
            recipient_list=recipient_list,
            html_message=html_message,  # HTML версия
            fail_silently=False
        )
        return True
    except Exception as e:
        print(f"Ошибка отправки письма: {e}")
        return False