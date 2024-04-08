from django import template

register = template.Library()

@register.filter
def addclass(field, css):
    return field.as_widget(attrs={'class': css})

@register.filter
def if_empty(var1, var2):
    if var1:
        return var1
    return var2
