import datetime as dt


def year(request):
    """
    Контекстный процессор, добавляющий текущий год в контекст шаблона.

    Возвращает словарь с текущим годом под ключом 'year'.
    """
    return {'year': dt.date.today().year}
