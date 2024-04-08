from rest_framework import views
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import filters
from rest_framework.decorators import action
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import (extend_schema_view, extend_schema,
                                   OpenApiParameter)

from reviews.models import Category, Genre, Title, Review, Comment
from .serializers import (SignUpSerializer, TokenObtainSerializer,
                          CategorySerializer, GenreSerializer, TitleSerializer,
                          TitleCreateUpdateSerializer, ReviewSerializer,
                          CommentSerializer, UserSerializer, UserMeSerializer)
from .permissions import (IsAdminOrReadOnly, IsAuthorOrAdminOrModeratorOrReadOnly,
                          IsAdmin)
from .mixins import ListCreateDestroyMixin
from .filters import TitleFilter

User = get_user_model()


@extend_schema(tags=['AUTH'])
class SignUpView(views.APIView):
    serializer_class = SignUpSerializer # Для drf_spectacular
    permission_classes = (AllowAny,)

    def send_code(self, user):
        send_mail(
            'Код подтверждения',
            f'{user.username}, ваш код подтверждения {user.confirmation_code}',
            None,
            (user.email,)
        )

    @extend_schema(summary='Регистрация нового пользователя',
                   description='Получить код подтверждения на переданный '
                               '``email``.')
    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            queryset = User.objects.all()
            username = serializer.validated_data.get('username')
            email = serializer.validated_data.get('email')
            code = get_random_string()
            try:
                user = queryset.get(username=username)
            except User.DoesNotExist:
                if not queryset.filter(email=email):
                    user = serializer.save(confirmation_code=code)
                    self.send_code(user)
                    return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                if user.email == email:
                    serializer.save(confirmation_code=code)
                    self.send_code(user)
                    return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=['AUTH'])
class TokenObtainRefreshView(views.APIView):
    serializer_class = TokenObtainSerializer # Для drf_spectacular
    permission_classes = (AllowAny,)

    @extend_schema(summary='Получение JWT-токена',
                   description='Получение JWT-токена в обмен на ``username`` '
                               'и ``confirmation code``.')
    def post(self, request):
        serializer = TokenObtainSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data.get('username')
            confirmation_code = serializer.validated_data.get(
                'confirmation_code'
            )
            user = get_object_or_404(User, username=username)
            if user.confirmation_code == confirmation_code:
                token = RefreshToken.for_user(user)
                data = {
                    'token': str(token.access_token)
                }
                return Response(data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=['CATEGORIES'])
@extend_schema_view(
    list=extend_schema(summary='Получение списка всех категорий',
                       description='Получить список всех категорий',
                       parameters=[
                           OpenApiParameter(
                               name='search',
                               description='Поиск по названию категории'
                           )
                       ]),
    create=extend_schema(summary='Добавление новой категории',
                         description='Создать категорию.'),
    destroy=extend_schema(summary='Удаление категории',
                          description='Удалить категорию.')
)
class CategoryViewSet(ListCreateDestroyMixin, viewsets.GenericViewSet):
    queryset = Category.objects.all()
    lookup_field = 'slug'
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


@extend_schema(tags=['GENRES'])
@extend_schema_view(
    list=extend_schema(summary='Получение списка всех жанров',
                       description='Получить список всех жанров.',
                       parameters=[
                           OpenApiParameter(
                               name='search',
                               description='Поиск по названию жанра'
                           )
                       ]),
    create=extend_schema(summary='Добавление жанра',
                         description='Добавить жанр.'),
    destroy=extend_schema(summary='Удаление жанра',
                          description='Удалить жанр.')
)
class GenreViewSet(ListCreateDestroyMixin, viewsets.GenericViewSet):
    queryset = Genre.objects.all()
    lookup_field = 'slug'
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


@extend_schema(tags=['TITLES'])
@extend_schema_view(
    list=extend_schema(summary='Получение списка всех произведений',
                       description='Получить список всех объектов.'),
    create=extend_schema(summary='Добавление произведения',
                         description='Добавить новое произведение.'),
    retrieve=extend_schema(summary='Получение информации о произведении',
                           description='Информация о произведении'),
    partial_update=extend_schema(summary='Частичное обновление информации о '
                                         'произведении',
                         description='Обновить информацию о произведении'),
    destroy=extend_schema(summary='Удаление произведения',
                          description='Удалить произведение.'),
    update=extend_schema(exclude=True)
)
class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(rating=Avg('reviews__score')).all()
    serializer_class = TitleSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleSerializer
        return TitleCreateUpdateSerializer


@extend_schema(tags=['REVIEWS'])
@extend_schema_view(
    list=extend_schema(summary='Получение списка всех отзывов',
                       description='Получить список всех отзывов.'),
    create=extend_schema(summary='Добавление нового отзыва',
                         description='Добавить новый отзыв. Пользователь может '
                                     'оставить только один отзыв на '
                                     'произведение.'),
    retrieve=extend_schema(summary='Полуение отзыва по id',
                           description='Получить отзыв по id для указанного '
                                       'произведения.'),
    partial_update=extend_schema(summary='Частичное обновление отзыва по id',
                         description='Частично обновить отзыв по id.'),
    destroy=extend_schema(summary='Удаление отзыва по id',
                          description='Удалить отзыв по id'),
    update=extend_schema(exclude=True)
)
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorOrAdminOrModeratorOrReadOnly,)

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        queryset = Review.objects.filter(title=title)
        return queryset

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        serializer.save(title=title, author=self.request.user)


@extend_schema(tags=['COMMENTS'])
@extend_schema_view(
    list=extend_schema(summary='Получение списка всех комментариев к отзыву',
                       description='Получить список всех комментариев к отзыву '
                                   'по id'),
    create=extend_schema(summary='Добавление комментария к отзыву',
                         description='Добавить новый комментарий для отзыва.'),
    retrieve=extend_schema(summary='Получение комментария к отзыву',
                           description='Получить комментарий для отзыва по '
                                       'id.'),
    partial_update=extend_schema(summary='Частичное обновление комментария к '
                                         'отзыву',
                         description='Частично обновить комментарий к отзыву '
                                     'по id.'),
    destroy=extend_schema(summary='Удаление комментария к отзыву',
                          description='Удалить комментарий к отзыву по id.'),
    update=extend_schema(exclude=True)
)
class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrAdminOrModeratorOrReadOnly,)

    def get_queryset(self):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, pk=review_id)
        queryset = Comment.objects.filter(review=review)
        return queryset

    def perform_create(self, serializer):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, pk=review_id)
        serializer.save(review=review, author=self.request.user)


@extend_schema_view(
    list=extend_schema(summary='Получение списка всех пользователей',
                       description='Получить список всех пользователей.'),
    create=extend_schema(summary='Добавление пользователя',
                         description='Добавить нового пользователя.'),
    retrieve=extend_schema(summary='Получение пользователя по username',
                          description='Получить пользователя по username.'),
    partial_update=extend_schema(summary='Изменение данных пользователя по '
                                         'username',
                                 description='Изменить данные пользователя '
                                              'по username.'),
    destroy=extend_schema(summary='Удаление пользователя по username',
                          description='Удалить пользователя по username.'),
    update=extend_schema(exclude=True),
)
@extend_schema(tags=['USERS'])
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    lookup_field = 'username'
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)

    @extend_schema(summary='Получение данных своей учетной записи',
                  description='Получить данные своей учетной записи')
    @action(detail=False, url_path='me',
            permission_classes=(IsAuthenticated,),
            serializer_class=UserMeSerializer)
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(summary='Изменение данных своей учетной записи',
                   description='Изменить данные своей учетной записи')
    @me.mapping.patch
    def me_partial_update(self, request):
        serializer = self.get_serializer(request.user, data=request.data,
                                         partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)
