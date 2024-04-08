from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from reviews.models import Category, Comment, Genre, Review, Title

User = get_user_model()


class ReviewViewsTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username='author')
        cls.category = Category.objects.create(name='category', slug='slug')
        cls.genre = Genre.objects.create(name='genre', slug='slug')
        cls.title = Title.objects.create(name='title', year=1900,
                                         category=cls.category)
        cls.title.genre.add(cls.genre)
        cls.review = Review.objects.create(author=cls.author, title=cls.title,
                                           text='text', score=10)
        cls.comment = Comment.objects.create(review=cls.review,
                                             author=cls.author, text='text')

    def setUp(self):
        self.user = User.objects.create(username='user')
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон"""
        template_page_names = {
            'reviews/index.html': reverse('reviews:index'),
            'reviews/title_detail.html': (
                reverse('reviews:title_detail', kwargs={'title_id': 1})
            ),
            'reviews/review_detail.html': (
                reverse('reviews:review_detail',
                        kwargs={'review_id': 1})
            ),
            'reviews/category_list.html': (
                reverse('reviews:category_list',
                        kwargs={'category_slug': 'slug'})
            ),
            'reviews/genre_list.html': (
                reverse('reviews:genre_list', kwargs={'genre_slug': 'slug'})
            ),
            'reviews/profile.html': (
                reverse('reviews:profile', kwargs={'username': 'author'})
            ),
            'reviews/search.html': reverse('reviews:search'),
        }
        for template, reverse_name in template_page_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом"""
        response = self.guest_client.get(reverse('reviews:index'))
        first_obj = response.context['page_obj'][0]
        title_name_0 = first_obj.name
        title_year_0 = first_obj.year
        title_category_0 = first_obj.category
        title_genre_0 = first_obj.genre.all()[0]
        self.assertEqual(title_name_0, 'title')
        self.assertEqual(title_year_0, 1900)
        self.assertEqual(title_category_0, self.category)
        self.assertEqual(title_genre_0, self.genre)

    def test_title_detail_page_show_correct_context(self):
        """Шаблон title_detail сформирован с правильным контекстом"""
        response = self.guest_client.get(
            reverse('reviews:title_detail', kwargs={'title_id': 1})
        )
        first_obj = response.context['page_obj'][0]
        review_author_0 = first_obj.author
        review_title_0 = first_obj.title
        review_text_0 = first_obj.text
        review_score_0 = first_obj.score
        self.assertEqual(review_author_0, self.author)
        self.assertEqual(review_title_0, self.title)
        self.assertEqual(review_text_0, 'text')
        self.assertEqual(review_score_0, 10)
        self.assertQuerysetEqual(
            response.context['page_obj'],
            Review.objects.filter(title=self.title)
        )

    def test_review_detail_page_show_correct_context(self):
        """Шаблон review_detail сформирован с правильным контекстом"""
        response = self.guest_client.get(
            reverse('reviews:review_detail',
                    kwargs={'review_id': 1})
        )
        first_obj = response.context['page_obj'][0]
        comment_review_0 = first_obj.review
        comment_author_0 = first_obj.author
        comment_text_0 = first_obj.text
        self.assertEqual(comment_review_0, self.review)
        self.assertEqual(comment_author_0, self.author)
        self.assertEqual(comment_text_0, 'text')
        self.assertQuerysetEqual(
            response.context['page_obj'],
            Comment.objects.filter(review=self.review)
        )

    def test_category_list_page_show_correct_template(self):
        """Шаблон category_list сформирован с правильным контекстом"""
        response = self.guest_client.get(
            reverse('reviews:category_list', kwargs={'category_slug': 'slug'})
        )
        first_obj = response.context['page_obj'][0]
        title_name_0 = first_obj.name
        title_year_0 = first_obj.year
        title_category_0 = first_obj.category
        title_genre_0 = first_obj.genre.all()[0]
        self.assertEqual(title_name_0, 'title')
        self.assertEqual(title_year_0, 1900)
        self.assertEqual(title_category_0, self.category)
        self.assertEqual(title_genre_0, self.genre)
        self.assertQuerysetEqual(
            response.context['page_obj'],
            Title.objects.filter(category=self.category)
        )

    def test_genre_list_page_show_correct_template(self):
        """Шаблон genre_list сформирован с правильным контекстом"""
        response = self.guest_client.get(
            reverse('reviews:genre_list', kwargs={'genre_slug': 'slug'})
        )
        first_obj = response.context['page_obj'][0]
        title_name_0 = first_obj.name
        title_year_0 = first_obj.year
        title_category_0 = first_obj.category
        title_genre_0 = first_obj.genre.all()[0]
        self.assertEqual(title_name_0, 'title')
        self.assertEqual(title_year_0, 1900)
        self.assertEqual(title_category_0, self.category)
        self.assertEqual(title_genre_0, self.genre)
        self.assertQuerysetEqual(
            response.context['page_obj'],
            Title.objects.filter(genre=self.genre)
        )

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контектом"""
        response = self.guest_client.get(
            reverse('reviews:profile', kwargs={'username': 'author'})
        )
        first_obj = response.context['page_obj'][0]
        review_author_0 = first_obj.author
        review_title_0 = first_obj.title
        review_text_0 = first_obj.text
        review_score_0 = first_obj.score
        self.assertEqual(review_author_0, self.author)
        self.assertEqual(review_title_0, self.title)
        self.assertEqual(review_text_0, 'text')
        self.assertEqual(review_score_0, 10)
        self.assertQuerysetEqual(
            response.context['page_obj'],
            Review.objects.filter(author=self.author)
        )
