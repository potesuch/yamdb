from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.views.generic.base import ContextMixin, TemplateResponseMixin
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import DeletionMixin, FormMixin, UpdateView
from django.views.generic.list import ListView

from .forms import CommentForm, ReviewForm
from .models import Category, Comment, Genre, Review, Title, User


class RelatedObjectView(TemplateResponseMixin, ContextMixin, View):
    """
    Представление для отображения связанных объектов на основе родительского объекта.

    Attributes:
        template_name (str): Путь к файлу шаблона для отображения представления.
        model (django.db.models.Model): Класс модели объекта.
        pk_url_kwarg (str): URL-ключевое слово для первичного ключа.
        slug_url_kwarg (str): URL-ключевое слово для slug.
        related_name (str): Название связанного атрибута в объекте.
        selected_fields (tuple): Кортеж полей, которые будут выбраны с помощью `select_related`.
        prefetched_fields (tuple): Кортеж полей, которые будут предварительно выбраны с помощью `prefetch_related`.
        context_object_name (str): Название переменной контекста для связанного объекта.
        context_objects_name (str): Название переменной контекста для связанных объектов.
        paginate_by (int): Количество элементов на странице при пагинации.
    """
    template_name = None
    model = None
    pk_url_kwarg = None
    slug_url_kwarg = None
    related_name = None
    selected_fields = (None,)
    prefetched_fields = (None,)
    context_object_name = None
    context_objects_name = None
    paginate_by = None
    paginate_orphans = 0

    def get_relations(self, related, selected_fields, prefetched_fields):
        """
        Получает связанные объекты с учетом выбранных и предварительно выбранных полей.

        Args:
            related (queryset): QuerySet связанных объектов.
            selected_fields (tuple): Кортеж полей для `select_related`.
            prefetched_fields (tuple): Кортеж полей для `prefetch_related`.

        Returns:
            queryset: QuerySet связанных объектов, оптимизированный с выбранными и предварительно выбранными полями.
        """
        if selected_fields:
            queryset = related.select_related(*selected_fields)
        if prefetched_fields:
            queryset = related.prefetch_related(*prefetched_fields)
        return queryset.all()

    def paginate_queryset(self, queryset, page_size):
        """
        Разбивает QuerySet на страницы с помощью пагинации.

        Args:
            queryset (queryset): QuerySet объектов для пагинации.
            page_size (int): Количество объектов на странице.

        Returns:
            Paginator: Объект Paginator для управления пагинацией.
            Page: Текущая страница.
            list: Список объектов на текущей странице.
            bool: Флаг, указывающий, есть ли страницы, кроме первой.
        """
        paginator = Paginator(queryset,
                              page_size,
                              orphans=self.paginate_orphans,
                              allow_empty_first_page=True)
        page_kwarg = 'page'
        page_number = self.kwargs.get(page_kwarg) or 1
        if page_number == 'last':
            page_number = paginator.num_pages
        else:
            page_number = int(page_number)
        page = paginator.page(page_number)
        return paginator, page, page.object_list, page.has_other_pages

    def get(self, request, *args, **kwargs):
        """
        Обрабатывает GET-запрос для отображения представления.

        Args:
            request (HttpRequest): Объект запроса.
            *args: Дополнительные позиционные аргументы.
            **kwargs: Дополнительные именованные аргументы.

        Returns:
            HttpResponse: Ответ на GET-запрос с отрендеренным представлением и контекстом.
        """
        context = self.get_context_data(**kwargs)
        pk = context.get(self.pk_url_kwarg)
        slug = context.get(self.slug_url_kwarg)
        username = context.get('username')
        if pk is not None:
            obj = get_object_or_404(self.model, pk=pk)
        elif slug is not None:
            obj = get_object_or_404(self.model, slug=slug)
        elif username is not None:
            obj = get_object_or_404(self.model, username=username)
        else:
            raise AttributeError
        related = getattr(obj, self.related_name)
        if self.selected_fields or self.prefetched_fields:
            queryset = self.get_relations(related, self.selected_fields,
                                          self.prefetched_fields)
        else:
            queryset = related.all()
        context[self.context_object_name or 'object'] = obj
        if queryset.exists() and self.paginate_by:
            paginator, page, queryset, is_paginated = self.paginate_queryset(
                queryset, self.paginate_by
            )
            context.update({
                'paginator': paginator,
                'page_obj': page,
                'is_paginated': is_paginated
            })
        context[self.context_objects_name or 'object_list'] = queryset
        return self.render_to_response(context)


class CreateView(LoginRequiredMixin, View):
    """
    Представление для создания новых объектов.

    Attributes:
        form_class (Form): Класс формы для создания объекта.
        related_model (django.db.models.Model): Класс связанной модели.
        related_model_pk_url_kwarg (str): URL-ключевое слово для первичного ключа .
        view_name (str): Имя представления, на которое перенаправляется после успешного создания.
        related_field (str): Имя поля связи между создаваемым и связанным объектом.
    """
    form_class = None
    related_model = None
    related_model_pk_url_kwarg = None
    view_name = None
    related_field = None

    def get_success_url(self):
        """
        Возвращает URL-адрес для перенаправления после успешного создания объекта.

        Returns:
            str: URL-адрес для перенаправления.
        """
        pk = self.kwargs.get(self.related_model_pk_url_kwarg)
        return reverse(self.view_name,
                       kwargs={self.related_model_pk_url_kwarg: pk})

    def form_valid(self, form):
        """
        Обрабатывает валидную форму для сохранения данных объекта.

        Args:
            form (Form): Валидная форма для создания объекта.

        Returns:
            HttpResponse: Ответ на успешное сохранение данных.
        """
        pk = self.kwargs.get(self.related_model_pk_url_kwarg)
        related_object = get_object_or_404(self.related_model, pk=pk)
        object = form.save(commit=False)
        object.author = self.request.user
        setattr(object, self.related_field, related_object)
        form.save()

    def post(self, request, *args, **kwargs):
        """
        Обрабатывает POST-запрос для создания объекта.

        Args:
            request (HttpRequest): Объект запроса.
            *args: Дополнительные позиционные аргументы.
            **kwargs: Дополнительные именованные аргументы.

        Returns:
            HttpResponse: Ответ на POST-запрос с перенаправлением на указанный URL-адрес.
        """
        form = self.form_class(self.request.POST or None)
        if form.is_valid():
            self.form_valid(form)
            return redirect(self.get_success_url())
        return redirect(reverse('reviews:index'))


class DeleteView(LoginRequiredMixin, SingleObjectMixin, DeletionMixin, View):
    """
    Представление для удаления объекта.

    Attributes:
        model (django.db.models.Model): Класс модели удаляемого объекта.
        pk_url_kwarg (str): URL-ключевое слово для первичного ключа объекта.
        related_model_pk_url_kwarg (str): URL-ключевое слово для первичного ключа связанного объекта.
        view_name (str): Имя представления, на которое перенаправляется после успешного удаления.
    """
    model = None
    pk_url_kwarg = None
    related_model_pk_url_kwarg = None
    view_name = None

    def get_success_url(self):
        """
        Возвращает URL-адрес для перенаправления после успешного удаления объекта.

        Returns:
            str: URL-адрес для перенаправления.
        """
        pk = self.kwargs.get(self.related_model_pk_url_kwarg)
        return reverse(self.view_name,
                       kwargs={self.related_model_pk_url_kwarg: pk})

    def delete(self, request, *args, **kwargs):
        """
        Обрабатывает DELETE-запрос для удаления объекта.

        Args:
            request (HttpRequest): Объект запроса.
            *args: Дополнительные позиционные аргументы.
            **kwargs: Дополнительные именованные аргументы.

        Returns:
            HttpResponse: Ответ на DELETE-запрос с перенаправлением на указанный URL-адрес.
        """
        self.object = self.get_object()
        user = self.request.user
        if self.object.author == user or user.role in ('admin', 'moderator'):
            success_url = self.get_success_url()
            self.object.delete()
            return redirect(success_url)
        return redirect(reverse('reviews:index'))


class IndexListView(ListView):
    """
    Представление для отображения списка произведений на главной странице.

    Атрибуты:
        template_name (str): Путь к файлу шаблона для отображения представления.
        context_object_name (str): Название переменной контекста для списка произведений.
        paginate_by (int): Количество произведений на одной странице при пагинации.
    """
    template_name = 'reviews/index.html'
    context_object_name = 'titles'
    paginate_by = 10

    def get_queryset(self):
        """
        Возвращает запрос для получения списка всех произведений с предварительной выборкой связанных объектов.

        Returns:
            QuerySet: Запрос для получения списка произведений.
        """
        return (Title.objects.all().select_related('category').
                prefetch_related('genre'))


class TitleDetailView(FormMixin, RelatedObjectView):
    """
    Представление для отображения деталей произведения.

    Атрибуты:
        template_name (str): Путь к файлу шаблона для отображения представления.
        model (django.db.models.Model): Класс модели произведения.
        pk_url_kwarg (str): URL-ключевое слово для первичного ключа произведения.
        related_name (str): Название связанного атрибута в модели произведения.
        selected_fields (tuple): Кортеж полей, которые будут выбраны с помощью `select_related`.
        context_object_name (str): Название переменной контекста для произведения.
        context_objects_name (str): Название переменной контекста для связанных объектов (отзывов).
        paginate_by (int): Количество элементов на странице при пагинации.
        form_class (Form): Класс формы для создания отзыва.
    """
    template_name = 'reviews/title_detail.html'
    model = Title
    pk_url_kwarg = 'title_id'
    related_name = 'reviews'
    selected_fields = ('author', 'title')
    context_object_name = 'title'
    context_objects_name = 'reviews'
    paginate_by = 5
    form_class = ReviewForm

    def get_context_data(self, **kwargs):
        """
        Добавляет дополнительные данные контекста для шаблона.

        Returns:
            dict: Словарь с дополнительными данными контекста.
        """
        context = super().get_context_data(**kwargs)
        pk = context.get(self.pk_url_kwarg)
        context['action_url'] = reverse('reviews:review_create',
                                        kwargs={self.pk_url_kwarg: pk})
        return context


class ReviewDetailView(FormMixin, RelatedObjectView):
    """
    Представление для отображения деталей отзыва.

    Атрибуты:
        template_name (str): Путь к файлу шаблона для отображения представления.
        model (django.db.models.Model): Класс модели отзыва.
        pk_url_kwarg (str): URL-ключевое слово для первичного ключа отзыва.
        related_name (str): Название связанного атрибута в модели отзыва.
        selected_fields (tuple): Кортеж полей, которые будут выбраны с помощью `select_related`.
        context_object_name (str): Название переменной контекста для отзыва.
        context_objects_name (str): Название переменной контекста для связанных объектов (комментариев).
        paginate_by (int): Количество элементов на странице при пагинации.
        form_class (Form): Класс формы для создания комментария.
    """
    template_name = 'reviews/review_detail.html'
    model = Review
    pk_url_kwarg = 'review_id'
    related_name = 'comments'
    selected_fields = ('review',)
    context_object_name = 'review'
    context_objects_name = 'comments'
    paginate_by = 10
    form_class = CommentForm

    def get_context_data(self, **kwargs):
        """
        Добавляет дополнительные данные контекста для шаблона.

        Returns:
            dict: Словарь с дополнительными данными контекста.
        """
        context = super().get_context_data(**kwargs)
        pk = context.get(self.pk_url_kwarg)
        context['action_url'] = reverse('reviews:comment_create',
                                        kwargs={self.pk_url_kwarg: pk})
        return context


class CategoryListView(RelatedObjectView):
    """
    Представление для отображения списка произведений по категориям.

    Атрибуты:
        template_name (str): Путь к файлу шаблона для отображения представления.
        model (django.db.models.Model): Класс модели категории.
        slug_url_kwarg (str): URL-ключевое слово для slug категории.
        related_name (str): Название связанного атрибута в модели категории.
        selected_fields (tuple): Кортеж полей, которые будут выбраны с помощью `select_related`.
        prefetched_fields (tuple): Кортеж полей, которые будут предварительно выбраны с помощью `prefetch_related`.
        context_object_name (str): Название переменной контекста для категории.
        context_objects_name (str): Название переменной контекста для связанных объектов (произведений).
        paginate_by (int): Количество элементов на странице при пагинации.
    """
    template_name = 'reviews/category_list.html'
    model = Category
    slug_url_kwarg = 'category_slug'
    related_name = 'titles'
    selected_fields = ('category',)
    prefetched_fields = ('genre',)
    context_object_name = 'category'
    context_objects_name = 'titles'
    paginate_by = 10


class GenreListView(RelatedObjectView):
    """
    Представление для отображения списка произведений по жанрам.

    Атрибуты:
        template_name (str): Путь к файлу шаблона для отображения представления.
        model (django.db.models.Model): Класс модели жанра.
        slug_url_kwarg (str): URL-ключевое слово для slug жанра.
        related_name (str): Название связанного атрибута в модели жанра.
        selected_fields (tuple): Кортеж полей, которые будут выбраны с помощью `select_related`.
        prefetched_fields (tuple): Кортеж полей, которые будут предварительно выбраны с помощью `prefetch_related`.
        context_object_name (str): Название переменной контекста для жанра.
        context_objects_name (str): Название переменной контекста для связанных объектов (произведений).
        paginate_by (int): Количество элементов на странице при пагинации.
    """
    template_name = 'reviews/genre_list.html'
    model = Genre
    slug_url_kwarg = 'genre_slug'
    related_name = 'title_set'
    selected_fields = ('category',)
    prefetched_fields = ('genre',)
    context_object_name = 'genre'
    context_objects_name = 'titles'
    paginate_by = 10


class ProfileView(RelatedObjectView):
    """
    Представление для отображения профиля пользователя.

    Атрибуты:
        template_name (str): Путь к файлу шаблона для отображения представления.
        model (django.db.models.Model): Класс модели пользователя.
        related_name (str): Название связанного атрибута в модели пользователя.
        selected_fields (tuple): Кортеж полей, которые будут выбраны с помощью `select_related`.
        context_object_name (str): Название переменной контекста для пользователя.
        context_objects_name (str): Название переменной контекста для связанных объектов (отзывов пользователя).
        paginate_by (int): Количество элементов на странице при пагинации.
    """
    template_name = 'reviews/profile.html'
    model = User
    related_name = 'reviews'
    selected_fields = ('author', 'title')
    context_object_name = 'author'
    context_objects_name = 'reviews'
    paginate_by = 10


class ReviewCreate(CreateView):
    """
    Представление для создания отзыва.

    Атрибуты:
        form_class (Form): Класс формы для создания отзыва.
        related_model (django.db.models.Model): Класс модели произведения (связанного объекта).
        related_model_pk_url_kwarg (str): URL-ключевое слово для первичного ключа связанного объекта.
        view_name (str): Имя представления, на которое перенаправляется после успешного создания отзыва.
        related_field (str): Имя поля связи между создаваемым отзывом и произведением.
    """
    form_class = ReviewForm
    related_model = Title
    related_model_pk_url_kwarg = 'title_id'
    view_name = 'reviews:title_detail'
    related_field = 'title'


class ReviewUpdate(LoginRequiredMixin, UpdateView):
    """
    Представление для обновления отзыва.

    Атрибуты:
        template_name (str): Путь к файлу шаблона для отображения представления.
        model (django.db.models.Model): Класс модели отзыва.
        pk_url_kwarg (str): URL-ключевое слово для первичного ключа отзыва.
        related_model_pk_url_kwarg (str): URL-ключевое слово для получения первичного ключа связанного объекта (произведения).
        fields (tuple): Кортеж полей, доступных для обновления.
    """
    template_name = 'reviews/review_update.html'
    model = Review
    pk_url_kwarg = 'review_id'
    related_model_pk_url_kwarg = 'title_id'
    fields = ('text', 'score')

    def get_success_url(self):
        review = self.object
        return reverse('reviews:title_detail',
                       kwargs={
                           self.related_model_pk_url_kwarg: review.title.id
                       })

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        user = self.request.user
        if self.object.author == user or user.role in ('admin', 'moderator'):
            return super().get(request, *args, **kwargs)
        return redirect(reverse('reviews:index'))

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        user = self.request.user
        if self.object.author == user or user.role in ('admin', 'moderator'):
            return super().post(request, *args, **kwargs)
        return redirect(reverse('reviews:index'))


class ReviewDelete(DeleteView):
    """
    Представление для удаления отзыва.

    Атрибуты:
        model (django.db.models.Model): Класс модели отзыва.
        pk_url_kwarg (str): URL-ключевое слово для первичного ключа отзыва.
        related_model_pk_url_kwarg (str): URL-ключевое слово для получения первичного ключа связанного объекта (произведения).
        view_name (str): Имя представления, на которое перенаправляется после успешного удаления отзыва.
    """
    model = Review
    pk_url_kwarg = 'review_id'
    related_model_pk_url_kwarg = 'title_id'
    view_name = 'reviews:title_detail'


class CommentCreate(CreateView):
    """
    Представление для создания комментария.

    Атрибуты:
        form_class (Form): Класс формы для создания комментария.
        related_model (django.db.models.Model): Класс модели отзыва (связанного объекта).
        related_model_pk_url_kwarg (str): URL-ключевое слово для первичного ключа связанного объекта (отзыва).
        view_name (str): Имя представления, на которое перенаправляется после успешного создания комментария.
        related_field (str): Имя поля связи между создаваемым комментарием и отзывом.
    """
    form_class = CommentForm
    related_model = Review
    related_model_pk_url_kwarg = 'review_id'
    view_name = 'reviews:review_detail'
    related_field = 'review'


class CommentDelete(DeleteView):
    """
    Представление для удаления комментария.

    Атрибуты:
        model (django.db.models.Model): Класс модели комментария.
        pk_url_kwarg (str): URL-ключевое слово для первичного ключа комментария.
        related_model_pk_url_kwarg (str): URL-ключевое слово для первичного ключа связанного объекта (отзыва).
        view_name (str): Имя представления, на которое перенаправляется после успешного удаления комментария.
    """
    model = Comment
    pk_url_kwarg = 'comment_id'
    related_model_pk_url_kwarg = 'review_id'
    view_name = 'reviews:review_detail'


class SearchView(ContextMixin, TemplateResponseMixin, View):
    """
    Представление для поиска отзывов по тексту.

    Атрибуты:
        template_name (str): Путь к файлу шаблона для отображения представления.
    """
    template_name = 'reviews/search.html'

    def get(self, request, *args, **kwargs):
        """
        Обрабатывает GET-запрос для выполнения поиска отзывов по тексту.

        Args:
            request (HttpRequest): Объект запроса.
            *args: Дополнительные позиционные аргументы.
            **kwargs: Дополнительные именованные аргументы.

        Returns:
            HttpResponse: Ответ на GET-запрос с отрендеренным представлением и контекстом.
        """
        q = self.request.GET.get('q')
        if q:
            reviews = Review.objects.filter(text__icontains=q)
        else:
            reviews = None
        context = self.get_context_data(**kwargs)
        context['reviews'] = reviews
        return self.render_to_response(context)
