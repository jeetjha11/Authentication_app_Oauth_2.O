from django.shortcuts import render, redirect
from django.contrib.auth import logout, user_logged_in, user_logged_out


# Create your views here.


def home_views(request):
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('/')


def dashboard_view(request):
    return render(request, 'dashboard.html')
