from django.contrib.auth import get_user_model
from django.test import TestCase
from reviews.models import Category, Comment, Genre, GenreTitle, Review, Title

User = get_user_model()


class ReviewModelTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        author = User.objects.create(username='author')
        cls.category = Category.objects.create(name='category',
                                               slug='slug')
        cls.genre = Genre.objects.create(name='genre', slug='slug')
        cls.title = Title.objects.create(name='title', year='1999',
                                         category=cls.category)
        cls.title.genre.add(cls.genre)
        cls.review = Review.objects.create(author=author,
                                           title=cls.title,
                                           text='12345678901234567890123',
                                           score='10')
        cls.comment = Comment.objects.create(review=cls.review, author=author,
                                             text='12345678901234567890123')
        cls.genretitle = GenreTitle.objects.get(genre=cls.genre,
                                                title=cls.title)

    def setUp(self):
        self.models = (
            self.category,
            self.genre,
            self.title,
            self.review,
            self.comment,
            self.genretitle
        )

    def test_moddels_correct_object_name(self):
        """Проверяем, что у моделей корректно работает __str__"""
        object_names = (
            'category',
            'genre',
            'title',
            '12345678901234567890...',
            '12345678901234567890...',
            'genre title',
        )
        for model, object_name in zip(self.models, object_names):
            with self.subTest(model=model):
                self.assertEqual(f'{model}', object_name)

    def test_models_correct_get_absolute_url(self):
        """Проверяем, что у моделей корректно работает get_absolute_url"""
        absolute_urls = (
            '/category/slug/',
            '/genre/slug/',
            '/titles/1/',
            '/reviews/1/',
        )
        for model, absolute_url in zip(self.models, absolute_urls):
            with self.subTest(model=model):
                self.assertEqual(model.get_absolute_url(), absolute_url)

    def test_models_correct_get_delete_url(self):
        """Проверяем, что у моделей корректно работает get_delete_url"""
        delete_urls = (
            '/titles/1/review/1/delete/',
            '/reviews/1/comment/1/delete/',
        )
        for model, delete_url in zip(self.models[3:4], delete_urls):
            with self.subTest(model=model):
                self.assertEqual(model.get_delete_url(), delete_url)
