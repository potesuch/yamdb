from django.contrib.auth.models import AbstractUser
from django.db import models

ROLES = (
    ('user', 'Пользователь'),
    ('moderator', 'Модератор'),
    ('admin', 'Администратор')
)


class User(AbstractUser):
    """
    Кастомная модель пользователя.

    Расширяет стандартную модель пользователя Django, добавляя дополнительные поля:
    - Поле email в качестве уникального идентификатора пользователя
    - Поле bio для описания профиля пользователя
    - Поле role для определения роли пользователя (Пользователь, Модератор, Администратор)
    - Поле confirmation_code для хранения кода подтверждения (используется для активации учетной записи)
    """
    email = models.EmailField('Почта', unique=True)
    bio = models.TextField('Описание', help_text='Введите описание профиля',
                           null=True, blank=True)
    role = models.CharField('Роль', max_length=20, choices=ROLES,
                            default='user')
    confirmation_code = models.CharField('Код подтверждения', max_length=12,
                                         null=True)

    @property
    def is_moderator(self):
        return self.role == 'moderator'

    @property
    def is_admin(self):
        return self.role == 'admin'
