import re
import datetime
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
    return render(request, "MainPage.html")

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

def send_welcome_email(email, firstname):
    """Отправка приветственного письма"""
    subject = 'Добро пожаловать в Онлайн библиотеку!'
    message = f'''
    Здравствуйте, {firstname}!

    Благодарим вас за регистрацию в нашей онлайн библиотеке.

    Ваш электронный читательский билет доступен в личном кабинете.

    С уважением,
    Команда Онлайн библиотеки
    '''
    from_email = 'daniil_projects@mail.ru'
    recipient_list = [email]

    try:
        send_mail(subject, message, from_email, recipient_list)
    except:
        pass
