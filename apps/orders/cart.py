from decimal import Decimal

from django.conf import settings

from apps.catalog.models import Product


class Cart:

    def __init__(self, request):
        self.session = request.session
        self.request = request
        cart = self.session.get(settings.CART_SESSION_KEY)
        if cart is None:
            cart = self.session[settings.CART_SESSION_KEY] = {}
        self.cart = cart

    def add(self, product, quantity=1, *, replace=False):
        key = str(product.pk)
        current = self.cart.get(key, {"quantity": 0})["quantity"]
        new_quantity = quantity if replace else current + quantity
        new_quantity = max(0, min(new_quantity, product.stock_quantity or 0))
        if new_quantity <= 0:
            self.cart.pop(key, None)
        else:
            self.cart[key] = {"quantity": new_quantity}
        self.save()
        return new_quantity

    def remove(self, product):
        self.cart.pop(str(product.pk), None)
        self.save()

    def clear(self):
        self.session[settings.CART_SESSION_KEY] = {}
        self.cart = self.session[settings.CART_SESSION_KEY]
        self.save()

    def save(self):
        self.session[settings.CART_SESSION_KEY] = self.cart
        self.session.modified = True

    def set_from_payload(self, payload):
        for raw_id, quantity in (payload or {}).items():
            try:
                product = Product.objects.active().get(pk=int(raw_id))
                quantity = int(quantity)
            except (Product.DoesNotExist, TypeError, ValueError):
                continue
            if quantity > 0:
                self.add(product, quantity)

    def merge_into_user(self, user):
        self.save()

    def get_items(self):
        product_ids = [int(pk) for pk in self.cart.keys() if str(pk).isdigit()]
        products = {
            p.pk: p
            for p in Product.objects.active().select_related("brand", "category").filter(pk__in=product_ids)
        }
        items, dirty = [], False
        for key in list(self.cart.keys()):
            product = products.get(int(key)) if str(key).isdigit() else None
            if product is None:
                self.cart.pop(key, None)
                dirty = True
                continue
            quantity = int(self.cart[key]["quantity"])
            stock = product.stock_quantity
            if quantity > stock:
                quantity = stock
                if quantity <= 0:
                    self.cart.pop(key, None)
                    dirty = True
                    continue
                self.cart[key] = {"quantity": quantity}
                dirty = True
            unit_price = product.final_price
            items.append({
                "product": product,
                "quantity": quantity,
                "unit_price": unit_price,
                "line_total": unit_price * quantity,
                "stock": stock,
            })
        if dirty:
            self.save()
        return items

    def __iter__(self):
        return iter(self.get_items())

    def __len__(self):
        return sum(int(item["quantity"]) for item in self.cart.values())

    @property
    def total_quantity(self):
        return len(self)

    @property
    def subtotal(self) -> Decimal:
        return sum((item["line_total"] for item in self.get_items()), Decimal(0))

    @property
    def is_empty(self):
        return not self.cart
