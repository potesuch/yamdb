from django.db import models
from django.contrib.auth.models import AbstractUser

ROLES = (
    ('user', 'Пользователь'),
    ('moderator', 'Модератор'),
    ('admin', 'Администратор')
)


class User(AbstractUser):
    email = models.EmailField('Почта', unique=True)
    bio = models.TextField('Описание', help_text='Введите описание профиля',
                           null=True, blank=True)
    role = models.CharField('Роль',max_length=20, choices=ROLES,
                            default='user')
    confirmation_code = models.CharField('Код подтверждения', max_length=12,
                                         null=True)

    @property
    def is_moderator(self):
        return self.role == 'moderator'

    @property
    def is_admin(self):
        return self.role == 'admin'
