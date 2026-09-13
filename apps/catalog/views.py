from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Avg, Count, F, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ReviewForm
from .models import Brand, Category, Product, Review, Supplier

SORT_OPTIONS = {
    "newest": ("-created_at", "Mới nhất"),
    "price_asc": ("effective_price", "Giá thấp → cao"),
    "price_desc": ("-effective_price", "Giá cao → thấp"),
    "name": ("name", "Tên A → Z"),
    "popular": ("-view_count", "Xem nhiều nhất"),
}


def _filtered_products(request):
    from django.db.models.functions import Coalesce

    qs = (
        Product.objects.active()
        .select_related("category", "brand")
        .annotate(
            effective_price=Coalesce("sale_price", "price"),
            stock_total=Coalesce(Sum("batches__quantity_remaining"), 0),
            rating_avg=Avg("reviews__rating"),
            reviews_total=Count("reviews", distinct=True),
        )
    )

    keyword = request.GET.get("q", "").strip()
    if keyword:
        qs = qs.filter(
            Q(name__icontains=keyword)
            | Q(sku__icontains=keyword)
            | Q(short_description__icontains=keyword)
            | Q(description__icontains=keyword)
            | Q(brand__name__icontains=keyword)
        )

    category_slug = request.GET.get("category", "").strip()
    if category_slug:
        category = Category.objects.filter(slug=category_slug).first()
        if category:
            child_ids = list(category.children.values_list("id", flat=True))
            qs = qs.filter(Q(category=category) | Q(category_id__in=child_ids))

    brand_slugs = [s for s in request.GET.getlist("brand") if s]
    if brand_slugs:
        qs = qs.filter(brand__slug__in=brand_slugs)

    for param, lookup in (("min_price", "effective_price__gte"), ("max_price", "effective_price__lte")):
        raw = request.GET.get(param, "").strip()
        if raw.isdigit():
            qs = qs.filter(**{lookup: int(raw)})

    if request.GET.get("in_stock") == "1":
        qs = qs.filter(stock_total__gt=0)
    if request.GET.get("on_sale") == "1":
        qs = qs.filter(sale_price__isnull=False, sale_price__lt=F("price"))

    sort_key = request.GET.get("sort", "newest")
    order_by = SORT_OPTIONS.get(sort_key, SORT_OPTIONS["newest"])[0]
    return qs.order_by(order_by), sort_key


def product_list(request):
    products, sort_key = _filtered_products(request)
    paginator = Paginator(products, 12)
    page = paginator.get_page(request.GET.get("page"))

    querystring = request.GET.copy()
    querystring.pop("page", None)

    context = {
        "page_obj": page,
        "products": page.object_list,
        "paginator": paginator,
        "categories": Category.objects.filter(is_active=True).select_related("parent"),
        "brands": Brand.objects.filter(is_active=True),
        "sort_options": SORT_OPTIONS,
        "current_sort": sort_key,
        "selected_category": request.GET.get("category", ""),
        "selected_brands": request.GET.getlist("brand"),
        "keyword": request.GET.get("q", ""),
        "min_price": request.GET.get("min_price", ""),
        "max_price": request.GET.get("max_price", ""),
        "in_stock": request.GET.get("in_stock") == "1",
        "on_sale": request.GET.get("on_sale") == "1",
        "querystring": querystring.urlencode(),
    }

    if request.headers.get("HX-Request"):
        return render(request, "catalog/partials/product_grid.html", context)
    return render(request, "catalog/product_list.html", context)


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.select_related("category", "brand", "supplier").prefetch_related("images", "batches"),
        slug=slug, is_active=True,
    )
    Product.objects.filter(pk=product.pk).update(view_count=F("view_count") + 1)

    reviews = product.reviews.filter(is_approved=True).select_related("user")
    my_review = reviews.filter(user=request.user).first() if request.user.is_authenticated else None

    related = (
        Product.objects.active()
        .filter(category=product.category)
        .exclude(pk=product.pk)
        .select_related("brand")[:8]
    )

    rating_breakdown = []
    total_reviews = reviews.count()
    for star in range(5, 0, -1):
        count = reviews.filter(rating=star).count()
        rating_breakdown.append({
            "star": star,
            "count": count,
            "percent": round(count / total_reviews * 100) if total_reviews else 0,
        })

    context = {
        "product": product,
        "reviews": reviews,
        "my_review": my_review,
        "review_form": ReviewForm(instance=my_review),
        "related_products": related,
        "rating_breakdown": rating_breakdown,
        "total_reviews": total_reviews,
    }
    return render(request, "catalog/product_detail.html", context)


def brand_list(request):
    brands = Brand.objects.filter(is_active=True).annotate(total_products=Count("products"))
    return render(request, "catalog/brand_list.html", {"brands": brands})


def supplier_list(request):
    suppliers = Supplier.objects.filter(is_active=True).annotate(total_products=Count("products"))
    return render(request, "catalog/supplier_list.html", {"suppliers": suppliers})


def supplier_detail(request, slug):
    supplier = get_object_or_404(Supplier, slug=slug, is_active=True)
    products = Product.objects.active().filter(supplier=supplier).select_related("brand")[:24]
    return render(request, "catalog/supplier_detail.html", {"supplier": supplier, "products": products})


@login_required
@require_POST
def review_create(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    if Review.objects.filter(product=product, user=request.user).exists():
        messages.warning(request, "Bạn đã đánh giá sản phẩm này rồi. Hãy chỉnh sửa đánh giá cũ.")
        return redirect(product.get_absolute_url())
    form = ReviewForm(request.POST)
    if form.is_valid():
        review = form.save(commit=False)
        review.product = product
        review.user = request.user
        review.save()
        messages.success(request, "Cảm ơn bạn đã đánh giá sản phẩm!")
    else:
        messages.error(request, "Đánh giá chưa hợp lệ, vui lòng kiểm tra lại.")
    return redirect(product.get_absolute_url())


@login_required
def review_update(request, pk):
    review = get_object_or_404(Review, pk=pk, user=request.user)
    form = ReviewForm(request.POST or None, instance=review)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Đã cập nhật đánh giá.")
        return redirect(review.product.get_absolute_url())
    return render(request, "catalog/review_form.html", {"form": form, "review": review})


@login_required
@require_POST
def review_delete(request, pk):
    review = get_object_or_404(Review, pk=pk, user=request.user)
    product_url = review.product.get_absolute_url()
    review.delete()
    messages.success(request, "Đã xóa đánh giá.")
    return redirect(request.POST.get("next") or product_url)
