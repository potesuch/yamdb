from django.test import TestCase, Client
from django.contrib.auth import get_user_model

from reviews.models import Category, Genre, Title, Review, Comment

User = get_user_model()


class ReviewURLTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username='author')
        category = Category.objects.create(name='category', slug='slug')
        genre = Genre.objects.create(name='genre', slug='slug')
        title = Title.objects.create(name='title', year=1999, category=category)
        title.genre.add(genre)
        review = Review.objects.create(author=cls.author,title=title, text='text',
                                       score=10)
        comment = Comment.objects.create(review=review, author=cls.author,
                                         text='text')
    def setUp(self):
        self.user = User.objects.create(username='user')
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author_client = Client()
        self.author_client.force_login(self.author)
        self.url_names_templates = {
            '/': 'reviews/index.html',
            '/titles/1/': 'reviews/title_detail.html',
            '/reviews/1/': 'reviews/review_detail.html',
            '/category/slug/': 'reviews/category_list.html',
            '/genre/slug/': 'reviews/genre_list.html',
            '/profile/author/': 'reviews/profile.html',
            '/search/': 'reviews/search.html',
        }
        self.urls= (
            '/titles/1/review/create/',
            '/titles/1/review/1/update/',
            '/titles/1/review/1/delete/',
            '/reviews/1/comment/',
            '/reviews/1/comment/1/delete/',
        )

    def test_urls_exist_at_desired_location_for_anonymous(self):
        """Страницы доступны ананимному пользователю"""
        for url in self.url_names_templates.keys():
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_urls_exist_at_desired_location_for_author(self):
        """Страницы доступны для пользователя автора"""
        response = self.author_client.get(
            self.urls[1],
            kwargs={'title_id': 1, 'review_id': 1}
        )
        self.assertEqual(response.status_code, 200)

    def test_urls_redirect_anonymous(self):
        """Страницы перенаправляют анонимного пользователя"""
        for url in self.urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertRedirects(
                    response,
                    f'/auth/login/?next={url}'
                )

    def test_urls_redirect_authorized(self):
        """Cтраницы перенаправляют авторизованного пользователя"""
        for url in self.urls:
            with self.subTest(url=url):
                response = self.authorized_client.post(url)
                self.assertRedirects(response, '/')

    def test_urls_uses_correct_template(self):
        for address, template in self.url_names_templates.items():
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertTemplateUsed(response, template)