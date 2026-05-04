import json
import os

import requests
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .models import UserProfile


FEEDBACK_SERVICE_URL = os.getenv('FEEDBACK_SERVICE_URL', 'http://localhost:5001')


def get_feedback_url(path):
    return f'{FEEDBACK_SERVICE_URL}{path}'


def home(request):
    return render(request, 'shop/home.html')


def products(request):
    return render(request, 'shop/products.html')


def about(request):
    return render(request, 'shop/about.html')


def contact(request):
    recent_feedbacks = []

    try:
        response = requests.get(get_feedback_url('/feedback/list'), timeout=3)
        if response.ok:
            recent_feedbacks = response.json().get('feedbacks', [])
    except requests.RequestException:
        recent_feedbacks = []

    context = {
        'recent_feedbacks': recent_feedbacks,
    }

    if request.user.is_authenticated:
        context.update({
            'user_name': request.user.first_name or request.user.username,
            'user_email': request.user.email,
        })

    return render(request, 'shop/contact.html', context)


def register(request):
    if request.method == 'POST':
        first_name = (request.POST.get('first_name') or '').strip()
        last_name = (request.POST.get('last_name') or '').strip()
        username = (request.POST.get('username') or '').strip()
        email = (request.POST.get('email') or '').strip()
        phone = (request.POST.get('phone') or '').strip()
        password = request.POST.get('password') or ''
        confirm_password = request.POST.get('confirm_password') or ''

        has_errors = False

        if username and User.objects.filter(username=username).exists():
            messages.error(request, 'Пользователь с таким логином уже существует.')
            has_errors = True

        if email and User.objects.filter(email=email).exists():
            messages.error(request, 'Пользователь с таким email уже существует.')
            has_errors = True

        if password != confirm_password:
            messages.error(request, 'Пароли не совпадают.')
            has_errors = True

        if len(password) < 8:
            messages.error(request, 'Пароль должен содержать минимум 8 символов.')
            has_errors = True

        if has_errors:
            return render(request, 'shop/register.html')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        UserProfile.objects.create(user=user, phone=phone)

        login(request, user)
        messages.success(request, f'Добро пожаловать, {user.first_name or user.username}! Регистрация прошла успешно.')
        return redirect('profile')

    return render(request, 'shop/register.html')


def user_login(request):
    if request.user.is_authenticated:
        return redirect('profile')

    if request.method == 'POST':
        username = request.POST.get('username') or ''
        password = request.POST.get('password') or ''

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'С возвращением, {user.first_name or user.username}!')
            next_url = request.GET.get('next', 'profile')
            return redirect(next_url)
        else:
            messages.error(request, 'Неверный логин или пароль.')

    return render(request, 'shop/login.html')


def user_logout(request):
    logout(request)
    messages.info(request, 'Вы вышли из аккаунта.')
    return redirect('home')


@login_required
def profile(request):
    user_profile = request.user.profile
    feedbacks = []

    try:
        response = requests.get(
            get_feedback_url('/feedback/by-email'),
            params={'email': request.user.email},
            timeout=3,
        )
        if response.ok:
            feedbacks = response.json().get('feedbacks', [])
    except requests.RequestException:
        feedbacks = []

    context = {
        'profile': user_profile,
        'feedbacks': feedbacks,
    }
    return render(request, 'shop/profile.html', context)


@require_POST
def feedback(request):
    is_json = 'application/json' in (request.content_type or '')

    if is_json:
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Невалидный JSON'}, status=400)
    else:
        data = {
            'name': request.POST.get('name'),
            'email': request.POST.get('email'),
            'message': request.POST.get('message'),
        }

    try:
        response = requests.post(
            get_feedback_url('/feedback'),
            json=data,
            timeout=3,
        )
        result = response.json()
    except requests.RequestException:
        result = {'status': 'error', 'message': 'Сервис обратной связи недоступен'}
        response = None

    if is_json or request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if response is not None and response.ok:
            return JsonResponse(result)
        return JsonResponse(result, status=400)

    if response is not None and response.ok:
        messages.success(request, 'Сообщение отправлено и сохранено через микросервис.')
    else:
        messages.error(request, result.get('message', 'Не удалось отправить сообщение.'))

    return redirect('contact')


def feedback_list(request):
    try:
        response = requests.get(get_feedback_url('/feedback/list'), timeout=3)
        if response.ok:
            return JsonResponse(response.json())
    except requests.RequestException:
        pass

    return JsonResponse({'feedbacks': []})