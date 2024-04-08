from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.validators import UnicodeUsernameValidator

from reviews.models import Category, Genre, Title, Review, Comment

User = get_user_model()


class SignUpSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    username = serializers.CharField(max_length=150,
                                     validators=(UnicodeUsernameValidator,),
                                     required=True)

    class Meta:
        model = User
        fields = ('email', 'username')

    def create(self, validated_data):
        code = validated_data.pop('confirmation_code')
        defaults = {'confirmation_code': code}
        instance, _ = User.objects.update_or_create(**validated_data,
                                                    defaults=defaults)
        return instance

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                'Имя пользователя не может быть me'
            )
        return value


class TokenObtainSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=150, required=True)

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')
        extra_kwargs = {'confirmation_code': {'required': True}}


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True)
    category = CategorySerializer()
    rating = serializers.IntegerField()

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating', 'description', 'genre',
                  'category')


class TitleCreateUpdateSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(slug_field='slug',
                                         queryset=Genre.objects.all(),
                                         many=True)
    category = serializers.SlugRelatedField(slug_field='slug',
                                            queryset=Category.objects.all())

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'genre', 'category')


class ReviewSerializer(serializers.ModelSerializer):
    title = serializers.HiddenField(default=serializers.SkipField())
    author = serializers.StringRelatedField()

    class Meta:
        model = Review
        fields = ('id', 'title', 'author', 'text', 'score', 'pub_date')
        read_only_fields = ('title', 'author')

    def validate(self, attrs):
        queryset = Review.objects.all()
        title = self.context.get('view').kwargs.get('title_id')
        author = self.context.get('request').user
        method = self.context.get('request').method
        if queryset.filter(title=title, author=author) and method == 'POST':
            raise serializers.ValidationError('Можно сделать только один обзор '
                                              'на один и тот же фильм.')
        return attrs


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()

    class Meta:
        model = Comment
        fields = ('id', 'review', 'author', 'text', 'pub_date')
        read_only_fields = ('review', 'author')


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'bio',
                  'role')


class UserMeSerializer(UserSerializer):

     class Meta(UserSerializer.Meta):
         read_only_fields = ('role',)
