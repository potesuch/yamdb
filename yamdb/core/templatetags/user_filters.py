from django import template

register = template.Library()


@register.filter
def addclass(field, css):
    """
    Фильтр для добавления CSS класса к полю формы.

    Принимает поле формы и строку с названием CSS класса.
    Возвращает поле формы с добавленным классом.
    """
    return field.as_widget(attrs={'class': css})


@register.filter
def if_empty(var1, var2):
    """
    Фильтр, возвращающий второе значение, если первое пустое.

    Принимает два аргумента: var1 и var2.
    Если var1 пустое, возвращает var2, иначе возвращает var1.
    """
    if var1:
        return var1
    return var2
