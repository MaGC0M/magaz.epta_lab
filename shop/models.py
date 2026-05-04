from django.db import models
from django.contrib.auth.models import User


class Feedback(models.Model):
    name = models.CharField('Имя', max_length=100)
    email = models.EmailField('Email')
    message = models.TextField('Сообщение')
    created_at = models.DateTimeField('Дата', auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Сообщение обратной связи'
        verbose_name_plural = 'Сообщения обратной связи'

    def __str__(self):
        return f'{self.name} ({self.email})'


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField('Телефон', max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'

    def __str__(self):
        return self.user.username
