from django.shortcuts import render

def home_page(request):
    return render(request, "MainPage.html")

def register_page(request):
    return render(request, "RegisterPage.html")
