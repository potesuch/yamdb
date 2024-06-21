import datetime as dt

from django.core.exceptions import ValidationError


def validate_year(value):
    """
    Проверка, что год не больше текущего.
    """
    now = dt.datetime.now().year
    if value > now:
        raise ValidationError('Год еще не наступил!')
    return value
