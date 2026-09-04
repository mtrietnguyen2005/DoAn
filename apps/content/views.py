from django.core.paginator import Paginator
from django.db.models import F, Q
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from .models import News, Promotion


def news_list(request):
    news = News.objects.filter(is_published=True, published_at__lte=timezone.now()).select_related("author")
    keyword = request.GET.get("q", "").strip()
    if keyword:
        news = news.filter(Q(title__icontains=keyword) | Q(summary__icontains=keyword) | Q(tags__icontains=keyword))
    page = Paginator(news, 9).get_page(request.GET.get("page"))
    return render(request, "content/news_list.html", {"page_obj": page, "news_list": page.object_list, "keyword": keyword})


def news_detail(request, slug):
    article = get_object_or_404(News, slug=slug, is_published=True)
    News.objects.filter(pk=article.pk).update(view_count=F("view_count") + 1)
    related = News.objects.filter(is_published=True).exclude(pk=article.pk)[:4]
    return render(request, "content/news_detail.html", {"article": article, "related_news": related})


def promotion_list(request):
    now = timezone.now()
    running = Promotion.objects.filter(is_active=True, start_date__lte=now, end_date__gte=now)
    upcoming = Promotion.objects.filter(is_active=True, start_date__gt=now)
    return render(request, "content/promotion_list.html", {"running_promotions": running, "upcoming_promotions": upcoming})


def promotion_detail(request, slug):
    promotion = get_object_or_404(Promotion, slug=slug, is_active=True)
    products = promotion.products.filter(is_active=True).select_related("brand", "category")
    return render(request, "content/promotion_detail.html", {"promotion": promotion, "products": products})
