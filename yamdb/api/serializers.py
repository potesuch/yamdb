from django.contrib.auth import get_user_model
from django.contrib.auth.validators import UnicodeUsernameValidator
from rest_framework import serializers
from reviews.models import Category, Comment, Genre, Review, Title

User = get_user_model()


class SignUpSerializer(serializers.ModelSerializer):
    """
    Сериализатор для регистрации нового пользователя.

    Поля:
    - email: Email пользователя (обязательное поле).
    - username: Имя пользователя (обязательное поле, макс. 150 символов, с валидацией по Unicode).
    """
    email = serializers.EmailField(required=True)
    username = serializers.CharField(max_length=150,
                                     validators=(UnicodeUsernameValidator,),
                                     required=True)

    class Meta:
        model = User
        fields = ('email', 'username')

    def create(self, validated_data):
        """
        Создание пользователя с подтверждением.

        Args:
            validated_data (dict): Проверенные данные.

        Returns:
            instance (User): Созданный экземпляр пользователя.
        """
        code = validated_data.pop('confirmation_code')
        defaults = {'confirmation_code': code}
        instance, _ = User.objects.update_or_create(**validated_data,
                                                    defaults=defaults)
        return instance

    def validate_username(self, value):
        """
        Проверка валидности имени пользователя.

        Проверяет, что имя пользователя не является "me".

        Args:
            value (str): Имя пользователя.

        Raises:
            serializers.ValidationError: Если имя пользователя равно "me".

        Returns:
            str: Валидное имя пользователя.
        """
        if value == 'me':
            raise serializers.ValidationError(
                'Имя пользователя не может быть me'
            )
        return value


class TokenObtainSerializer(serializers.ModelSerializer):
    """
    Сериализатор для получения JWT-токена.

    Поля:
    - username: Имя пользователя (обязательное поле).
    - confirmation_code: Код подтверждения (обязательное поле).
    """
    username = serializers.CharField(max_length=150, required=True)

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')
        extra_kwargs = {'confirmation_code': {'required': True}}


class CategorySerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Категории (Category).

    Поля:
    - name: Название категории.
    - slug: Уникальный идентификатор категории.
    """

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Жанра (Genre).

    Поля:
    - name: Название жанра.
    - slug: Уникальный идентификатор жанра.
    """

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Произведения (Title).

    Поля:
    - id: Уникальный идентификатор произведения.
    - name: Название произведения.
    - year: Год выпуска произведения.
    - rating: Рейтинг произведения.
    - description: Описание произведения.
    - genre: Сериализатор жанра (GenreSerializer), связанный через внешний ключ многие ко многим.
    - category: Сериализатор категории (CategorySerializer), связанный через внешний ключ.
    """
    genre = GenreSerializer(many=True)
    category = CategorySerializer()
    rating = serializers.IntegerField()

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating', 'description', 'genre',
                  'category')


class TitleCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания и обновления Произведения (Title).

    Поля:
    - id: Уникальный идентификатор произведения.
    - name: Название произведения.
    - year: Год выпуска произведения.
    - description: Описание произведения.
    - genre: Сериализатор жанра (SlugRelatedField), связанный через внешний ключ многие ко многим.
    - category: Сериализатор категории (SlugRelatedField), связанный через внешний ключ.
    """
    genre = serializers.SlugRelatedField(slug_field='slug',
                                         queryset=Genre.objects.all(),
                                         many=True)
    category = serializers.SlugRelatedField(slug_field='slug',
                                            queryset=Category.objects.all())

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'genre', 'category')


class ReviewSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Отзыва (Review).

    Поля:
    - id: Уникальный идентификатор отзыва.
    - title: Скрытое поле произведения (HiddenField).
    - author: Строковое представление автора отзыва.
    - text: Текст отзыва.
    - score: Оценка отзыва.
    - pub_date: Дата публикации отзыва.
    """
    title = serializers.HiddenField(default=serializers.SkipField())
    author = serializers.StringRelatedField()

    class Meta:
        model = Review
        fields = ('id', 'title', 'author', 'text', 'score', 'pub_date')
        read_only_fields = ('title', 'author')

    def validate(self, attrs):
        """
        Проверка на дублирование отзыва.

        Пользователь может оставить только один отзыв на одно и то же произведение.

        Args:
            attrs (dict): Проверенные данные.

        Raises:
            serializers.ValidationError: Если пользователь пытается оставить несколько отзывов на одно и то же произведение.

        Returns:
            dict: Валидные данные отзыва.
        """
        queryset = Review.objects.all()
        title = self.context.get('view').kwargs.get('title_id')
        author = self.context.get('request').user
        method = self.context.get('request').method
        if queryset.filter(title=title, author=author) and method == 'POST':
            raise serializers.ValidationError('Можно сделать только один '
                                              'обзор на один и тот же фильм.')
        return attrs


class CommentSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Комментария (Comment).

    Поля:
    - id: Уникальный идентификатор комментария.
    - review: Скрытое поле отзыва (HiddenField).
    - author: Строковое представление автора комментария.
    - text: Текст комментария.
    - pub_date: Дата публикации комментария.
    """
    author = serializers.StringRelatedField()

    class Meta:
        model = Comment
        fields = ('id', 'review', 'author', 'text', 'pub_date')
        read_only_fields = ('review', 'author')


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Пользователя (User).

    Поля:
    - username: Имя пользователя.
    - email: Email пользователя.
    - first_name: Имя пользователя.
    - last_name: Фамилия пользователя.
    - bio: Описание пользователя.
    - role: Роль пользователя.
    """

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'bio',
                  'role')


class UserMeSerializer(UserSerializer):
    """
    Сериализатор для текущего пользователя (User), представление только для чтения.

    Поля:
    - username: Имя пользователя.
    - email: Email пользователя.
    - first_name: Имя пользователя.
    - last_name: Фамилия пользователя.
    - bio: Описание пользователя.
    """

    class Meta(UserSerializer.Meta):
        read_only_fields = ('role',)
