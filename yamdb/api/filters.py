from django_filters import rest_framework as filters
from reviews.models import Title


class TitleFilter(filters.FilterSet):
    """
    Фильтр для произведений.

    Позволяет фильтровать произведения по категории, названию, жанру и году.
    """
    category = filters.CharFilter(field_name='category__slug')
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    genre = filters.CharFilter(field_name='genre__slug')

    class Meta:
        model = Title
        fields = ('category', 'name', 'genre', 'year')
