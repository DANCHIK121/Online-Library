import re
from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import authenticate, login as auth_login

# Render pages
def home_page(request):
    return render(request, "MainPage.html")

def register_page(request):
    return render(request, "RegisterPage.html")

def login_page(request):
    return render(request, "LoginPage.html")

# Handlers for pages work
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
            user = User.objects.create(
                username=username,
                email=email,
                password=password,
                first_name=firstname,
                last_name=lastname
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
            # send_welcome_email(email, firstname)

            # Automatic login after registration
            # login(request, user)

            # Success Message
            messages.success(request, f'Добро пожаловать, {firstname}! Регистрация прошла успешно.')

            # Перенаправление на страницу читательского билета или главную
            return redirect('home')  # или 'profile'

        except Exception as e:
            messages.error(request, f'Ошибка при регистрации: {str(e)}')
            return render(request, 'RegisterPage.html', {'form_data': request.POST})

    return render(request, 'RegisterPage.html')

@csrf_protect
def login(request):
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
                    auth_login(request, authenticated_user)

                    # Setting up a session
                    if not remember_me:
                        request.session.set_expiry(0)  # The session expires when the browser is closed

                    messages.success(request, f'Добро пожаловать, {authenticated_user.username}!')
                    return redirect('home')
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
#     from_email = 'noreply@library.com'  # Укажите ваш email
#     recipient_list = [email]
#
#     try:
#         send_mail(subject, message, from_email, recipient_list)
#     except:
#         pass
