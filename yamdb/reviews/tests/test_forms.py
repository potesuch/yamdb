from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from reviews.models import Category, Comment, Genre, Review, Title

User = get_user_model()


class ReviewFormTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username='author')
        category = Category.objects.create(name='category', slug='slug')
        genre = Genre.objects.create(name='genre', slug='slug')
        title = Title.objects.create(name='title', year=1900,
                                     category=category)
        title.genre.add(genre)
        review = Review.objects.create(author=cls.author, title=title,
                                       text='text', score=10)
        Comment.objects.create(review=review, author=cls.author, text='text')

    def setUp(self):
        self.user = User.objects.create(username='user', email='user@user.us')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author_client = Client()
        self.author_client.force_login(self.author)

    def test_create_review(self):
        """Валидная форма создает запись в review"""
        review_cnt = Review.objects.count()
        form_data = {
            'text': 'create',
            'score': 1
        }
        response = self.authorized_client.post(
            reverse('reviews:review_create', kwargs={'title_id': 1}),
            form_data
        )
        self.assertEqual(Review.objects.count(), review_cnt + 1)
        self.assertRedirects(
            response,
            reverse('reviews:title_detail', kwargs={'title_id': 1})
        )
        self.assertTrue(
            Review.objects.filter(author=self.user, **form_data).exists()
        )

    def test_update_review(self):
        """Валидная форма редактирует запись в review"""
        form_data = {
            'text': 'update',
            'score': 1
        }
        response = self.author_client.post(
            reverse('reviews:review_update',
                    kwargs={'title_id': 1, 'review_id': 1}),
            form_data
        )
        self.assertRedirects(
            response,
            reverse('reviews:title_detail', kwargs={'title_id': 1})
        )
        self.assertTrue(
            Review.objects.filter(author=self.author, **form_data).exists()
        )

    def test_create_comment(self):
        """Валидная форма создает запись в comment"""
        comment_cnt = Comment.objects.count()
        form_data = {
            'text': 'create'
        }
        response = self.authorized_client.post(
            reverse('reviews:comment_create', kwargs={'review_id': 1}),
            form_data
        )
        self.assertTrue(Comment.objects.count(), comment_cnt + 1)
        self.assertRedirects(
            response,
            reverse('reviews:review_detail', kwargs={'review_id': 1})
        )
        self.assertTrue(
            Comment.objects.filter(author=self.user, **form_data)
        )
