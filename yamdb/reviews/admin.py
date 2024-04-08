from django.contrib import admin

from .models import Category, Comment, Genre, GenreTitle, Review, Title


class GenresInline(admin.TabularInline):
    model = GenreTitle
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    list_display_links = ('name',)
    list_editable = ('slug',)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    list_display_links = ('name',)
    list_editable = ('slug',)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    inlines = (GenresInline,)
    list_display = ('name', 'year', 'category', 'get_genres')
    list_display_links = ('name',)
    list_filter = ('category', 'genre')
    search_fields = ('name', 'year')
    ordering = ('name',)

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('genre')

    @admin.display(description='genres')
    def get_genres(self, obj):
        return ','.join(genre.name for genre in obj.genre.all())


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('author', 'get_text', 'score', 'title')
    list_display_links = ('get_text',)
    search_fields = ('author', 'get_text', 'title')
    ordering = ('title',)

    def get_text(self, obj):
        return f'{obj.text[:20]}...'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'get_text', 'get_review_title',
                    'get_review_author')
    list_display_links = ('get_text',)
    search_fields = ('author', 'get_text', 'get_review_title',
                     'get_review_author')
    ordering = ('review__title',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('review')

    @admin.display(description='text')
    def get_text(self, obj):
        return f'{obj.text[:20]}...'

    @admin.display(description='title')
    def get_review_title(self, obj):
        return obj.review.title

    @admin.display(description='review author')
    def get_review_author(self, obj):
        return obj.review.author
