# Рецензии на произведения

API для системы рецензий на произведения: фильмы, книги, музыка и прочее.

## Описание

Этот проект представляет собой API для платформы рецензирования различных произведений. Пользователи могут просматривать список произведений, оставлять отзывы и комментарии, добавлять новые произведения, управлять пользователями и многое другое.

## Основные возможности

- Получение списка произведений, фильтрация и поиск по различным параметрам (например, категория, жанр, год выпуска).
- Добавление новых произведений с указанием категории, жанров и прочих характеристик.
- Оставление отзывов и комментариев к произведениям.
- Регистрация и аутентификация пользователей с помощью JWT-токенов.
- Управление пользователями: просмотр, обновление, удаление данных своего профиля и просмотр других пользователей (для администраторов).
- Защита API с помощью различных уровней доступа: доступ только для чтения, доступ для администраторов и разработчиков, доступ для автора отзыва/комментария и т.д.

## Технологии

Проект реализован с использованием следующих технологий:

- **Django** - веб-фреймворк для Python.
- **Django REST Framework** - мощный инструмент для создания API на основе Django.
- **Django REST Framework SimpleJWT** - библиотека для генерации JWT-токенов.
- **PostgreSQL** - реляционная база данных для хранения данных.
- **drf-spectacular** - инструмент для автоматической генерации документации OpenAPI.
- **Docker** - платформа для создания, развертывания и управления контейнерами.
- **GitHub Actions** - сервис для автоматизации сборки, тестирования и развертывания проекта.

## Установка и запуск

Чтобы установить и запустить проект локально, выполните следующие шаги:

1. Клонирование репозитория:

``` sh

git clone https://github.com/your/repository.git
cd repository
```

2. Установка зависимостей:

Рекомендуется использовать виртуальное окружение. Установите зависимости, выполнив:

``` sh

pip install -r requirements.txt
```

3. Настройка базы данных:

Создайте базу данных PostgreSQL и настройте подключение в файле settings.py.

4. Применение миграций:

Примените миграции для создания таблиц в базе данных:

``` sh

python manage.py migrate
```

5. Запуск сервера:

Запустите сервер разработки Django:

``` sh

python manage.py runserver
```

После этого API будет доступно по адресу [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

## Документация API

Документация API сгенерирована с использованием drf-spectacular и доступна по адресу [http://127.0.0.1:8000/api/schema/swagger-ui/](http://127.0.0.1:8000/api/schema/swagger-ui/).
