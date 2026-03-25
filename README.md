Online Library on Python Django

Шаги для запуска сервера:
1) Скопировать этот репозиторий по ссылке https://github.com/DANCHIK121/Online-Library
2) Зайти в папку репозитория
3) Открыть эту папку в консоли
4) Ввести команду pip install -r requirements.txt
5) Ввести команду python manage.py runserver
6) Установить программу cloudpub
7) Нажать на кнопку добавить и ввести там localhost и порт 8000
8) Скопировать хост и вставить его в список ALLOWED_HOSTS в файле settings.py
9) Также добавить ссылку на сайта вида https://домен в список CSRF_TRUSTED_ORIGINS в файле settings.py
10) Перейти по ссылке из cloudpub