from django.db.models import Avg, Count, Sum
from django.db.models.functions import Coalesce
from django.shortcuts import render
from django.utils import timezone

from apps.catalog.models import Brand, Category, Product
from apps.content.models import Banner, News, Promotion


def _annotated_products():
    return Product.objects.active().select_related("brand", "category").annotate(
        stock_total=Coalesce(Sum("batches__quantity_remaining"), 0),
        rating_avg=Avg("reviews__rating"),
        reviews_total=Count("reviews", distinct=True),
    )


def home(request):
    now = timezone.now()
    context = {
        "banners": Banner.objects.filter(
            is_active=True, position=Banner.Position.HERO, start_date__lte=now
        ).exclude(end_date__lt=now),
        "featured_products": _annotated_products().filter(is_featured=True)[:8],
        "new_products": _annotated_products().order_by("-created_at")[:8],
        "sale_products": _annotated_products().filter(sale_price__isnull=False).order_by("-created_at")[:8],
        "categories": Category.objects.filter(is_active=True, parent__isnull=True).annotate(
            total_products=Count("products")
        )[:12],
        "brands": Brand.objects.filter(is_active=True)[:12],
        "promotions": Promotion.objects.filter(is_active=True, start_date__lte=now, end_date__gte=now)[:3],
        "latest_news": News.objects.filter(is_published=True, published_at__lte=now)[:4],
    }
    return render(request, "core/home.html", context)


def about(request):
    return render(request, "core/about.html")


def contact(request):
    return render(request, "core/contact.html")
