from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse

from .validators import validate_year

User = get_user_model()


class PubDateModel(models.Model):
    """
    Абстрактная модель с датой публикации.

    Добавляет поле даты публикации к модели.
    """
    pub_date = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        abstract = True


class Category(models.Model):
    """
    Модель для категорий произведений.

    Определяет категорию произведения с уникальным slug и методы для получения URL.
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('reviews:category_list',
                       kwargs={'category_slug': self.slug})


class Genre(models.Model):
    """
    Модель для жанров произведений.

    Определяет жанр произведения с уникальным slug и методы для получения URL.
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('reviews:genre_list',
                       kwargs={'genre_slug': self.slug})


class Title(models.Model):
    """
    Модель для произведений.

    Определяет название, год выпуска, категорию, жанры и описание произведения.
    """
    name = models.CharField(max_length=100)
    year = models.PositiveSmallIntegerField('Год')
    category = models.ForeignKey(Category, on_delete=models.CASCADE,
                                 related_name='titles',
                                 validators=(validate_year,))
    genre = models.ManyToManyField(Genre, through='GenreTitle')
    description = models.TextField('Описание', null=True, blank=True)

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ('-year',)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('reviews:title_detail', kwargs={'title_id': self.pk})


class GenreTitle(models.Model):
    """
    Промежуточная модель для связи жанров и произведений.

    Определяет связь между жанром и произведением.
    """
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    title = models.ForeignKey(Title, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Жанр - Произведение'
        verbose_name_plural = 'Жанры - Произведения'

    def __str__(self):
        return f'{self.genre} {self.title}'


class Review(PubDateModel):
    """
    Модель для отзывов к произведениям.

    Определяет текст отзыва, оценку, автора и произведение, к которому относится отзыв.
    """
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='reviews')
    title = models.ForeignKey(Title, on_delete=models.CASCADE,
                              related_name='reviews')
    text = models.TextField('Отзыв', help_text='Введите текст отзыва')
    score = models.PositiveSmallIntegerField(
        'Оценка',
        help_text='Выберите оценку',
        choices=((i, i) for i in range(11))
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ('-pub_date',)
        constraints = (
            models.UniqueConstraint(
                fields=('author', 'title'),
                name='unique_review_author'
            ),
        )

    def __str__(self):
        return f'{self.text[:20]}...'

    def get_absolute_url(self):
        return reverse('reviews:review_detail', kwargs={'review_id': self.pk})

    def get_delete_url(self):
        return reverse(
            'reviews:review_delete',
            kwargs={'title_id': self.title.id, 'review_id': self.pk}
        )


class Comment(PubDateModel):
    """
    Модель для комментариев к отзывам.

    Определяет текст комментария, автора и отзыв, к которому относится комментарий.
    """
    review = models.ForeignKey(Review, on_delete=models.CASCADE,
                               related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='comments')
    text = models.TextField('Комментарий',
                            help_text='Введите текст комментария')

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('-pub_date',)

    def __str__(self):
        return f'{self.text[:20]}...'

    def get_delete_url(self):
        return reverse(
            'reviews:comment_delete',
            kwargs={'review_id': self.review.id, 'comment_id': self.pk}
        )
