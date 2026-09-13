from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def vnd(value):
    try:
        return f"{int(value):,}".replace(",", ".") + "đ"
    except (TypeError, ValueError):
        return value


@register.filter
def stars(rating):
    try:
        rating = int(round(float(rating or 0)))
    except (TypeError, ValueError):
        rating = 0
    return mark_safe("★" * rating + '<span class="text-slate-300">' + "★" * (5 - rating) + "</span>")


@register.simple_tag(takes_context=True)
def query_replace(context, **kwargs):
    query = context["request"].GET.copy()
    for key, value in kwargs.items():
        if value in (None, ""):
            query.pop(key, None)
        else:
            query[key] = value
    if "page" not in kwargs:
        query.pop("page", None)
    return query.urlencode()


@register.filter
def get_item(dictionary, key):
    if hasattr(dictionary, "get"):
        return dictionary.get(key)
    return None


@register.filter
def subtract(value, arg):
    try:
        return value - arg
    except TypeError:
        return value
