from django.shortcuts import render
from django.views import View
from django.views.generic.base import ContextMixin, TemplateResponseMixin
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView, FormMixin, DeletionMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse

from .models import Title, Category, Genre, Review, User, Comment
from .forms import ReviewForm, CommentForm


class RelatedObjectView(TemplateResponseMixin, ContextMixin, View):
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
        queryset = related.all()
        if selected_fields:
            queryset = queryset.select_related(*selected_fields)
        if prefetched_fields:
            queryset = queryset.prefetch_related(*prefetched_fields)
        return queryset

    def paginate_queryset(self, queryset, page_size):
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
    form_class = None
    related_model = None
    related_model_pk_url_kwarg = None
    view_name = None
    related_field = None

    def get_success_url(self):
        pk = self.kwargs.get(self.related_model_pk_url_kwarg)
        url = reverse(self.view_name,
                      kwargs={self.related_model_pk_url_kwarg: pk})
        return url

    def form_valid(self, form):
        pk = self.kwargs.get(self.related_model_pk_url_kwarg)
        related_object = get_object_or_404(self.related_model, pk=pk)
        object = form.save(commit=False)
        object.author = self.request.user
        setattr(object, self.related_field, related_object)
        form.save()

    def post(self, request, *args, **kwargs):
        form = self.form_class(self.request.POST or None)
        if form.is_valid():
            self.form_valid(form)
            return redirect(self.get_success_url())
        return redirect(reverse('reviews:index'))


class DeleteView(LoginRequiredMixin, SingleObjectMixin, DeletionMixin, View):
    model = None
    pk_url_kwarg = None
    related_model_pk_url_kwarg = None
    view_name = None

    def get_success_url(self):
        pk = self.kwargs.get(self.related_model_pk_url_kwarg)
        url = reverse(self.view_name,
                      kwargs={self.related_model_pk_url_kwarg: pk})
        return url

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        user = self.request.user
        if self.object.author == user or user.role in ('admin', 'moderator'):
            success_url = self.get_success_url()
            self.object.delete()
            return redirect(success_url)
        return redirect(reverse('reviews:index'))


class IndexListView(ListView):
    template_name = 'reviews/index.html'
    context_object_name = 'titles'
    paginate_by = 10

    def get_queryset(self):
        queryset = (Title.objects.all().select_related('category').
                    prefetch_related('genre'))
        return queryset


class TitleDetailView(FormMixin, RelatedObjectView):
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
        context = super().get_context_data(**kwargs)
        pk = context.get(self.pk_url_kwarg)
        context['action_url'] = reverse('reviews:review_create',
                                        kwargs={self.pk_url_kwarg: pk})
        return context


class ReviewDetailView(FormMixin, RelatedObjectView):
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
        context = super().get_context_data(**kwargs)
        pk = context.get(self.pk_url_kwarg)
        context['action_url'] = reverse('reviews:comment_create',
                                        kwargs={self.pk_url_kwarg: pk})
        return context


class CategoryListView(RelatedObjectView):
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
    template_name = 'reviews/profile.html'
    model = User
    related_name = 'reviews'
    selected_fields = ('author', 'title')
    context_object_name = 'author'
    context_objects_name = 'reviews'
    paginate_by = 10


class ReviewCreate(CreateView):
    form_class = ReviewForm
    related_model = Title
    related_model_pk_url_kwarg = 'title_id'
    view_name = 'reviews:title_detail'
    related_field = 'title'


class ReviewUpdate(LoginRequiredMixin, UpdateView):
    template_name = 'reviews/review_update.html'
    model = Review
    pk_url_kwarg = 'review_id'
    related_model_pk_url_kwarg = 'title_id'
    fields = ('text', 'score')

    def get_success_url(self):
        review = self.object
        url = reverse('reviews:title_detail',
                      kwargs={self.related_model_pk_url_kwarg: review.title.id})
        return url

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
    model = Review
    pk_url_kwarg = 'review_id'
    related_model_pk_url_kwarg = 'title_id'
    view_name = 'reviews:title_detail'


class CommentCreate(CreateView):
    form_class = CommentForm
    related_model = Review
    related_model_pk_url_kwarg = 'review_id'
    view_name = 'reviews:review_detail'
    related_field = 'review'


class CommentDelete(DeleteView):
    model = Comment
    pk_url_kwarg = 'comment_id'
    related_model_pk_url_kwarg = 'review_id'
    view_name = 'reviews:review_detail'


class SearchView(ContextMixin, TemplateResponseMixin, View):
    template_name = 'reviews/search.html'

    def get(self, request, *args, **kwargs):
        q = self.request.GET.get('q')
        if q:
            reviews = Review.objects.filter(text__icontains=q)
        else:
            reviews = None
        context = self.get_context_data(**kwargs)
        context['reviews'] = reviews
        return self.render_to_response(context)
