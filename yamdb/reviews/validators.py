import datetime as dt
from django.core.exceptions import ValidationError

def validate_year(value):
    now = dt.datetime.now().year
    if value > now:
        raise ValidationError('Год еще не наступил!')
    return value
