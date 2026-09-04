"""Kiểm thử nghiệp vụ đơn hàng: COGS, đổi trạng thái, hủy đơn và hoàn kho."""
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from apps.catalog.models import Brand, Category, Product
from apps.inventory.models import Batch
from apps.orders.models import Order, PromoCode
from apps.orders.services import OrderError, cancel_order, change_order_status, create_order

User = get_user_model()


class FakeCart:
    """Giỏ hàng giả lập để kiểm thử service tạo đơn."""

    def __init__(self, items):
        self._items = items
        self.cleared = False

    def get_items(self):
        return self._items

    def clear(self):
        self.cleared = True


class OrderServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="khach", email="khach@test.vn", password="matkhau123")
        self.category = Category.objects.create(name="RAM")
        self.brand = Brand.objects.create(name="Kingston")
        self.product = Product.objects.create(
            name="RAM DDR5 16GB", sku="RAM001", category=self.category, brand=self.brand, price=Decimal(1500000)
        )
        today = timezone.localdate()
        self.batch_a = Batch.objects.create(
            product=self.product, batch_code="RA1", quantity_in=4, quantity_remaining=4,
            cost_price=Decimal(1000000), expiry_date=today + timedelta(days=10),
        )
        self.batch_b = Batch.objects.create(
            product=self.product, batch_code="RA2", quantity_in=10, quantity_remaining=10,
            cost_price=Decimal(1200000), expiry_date=today + timedelta(days=200),
        )

    def _cart(self, quantity=2):
        return FakeCart([{
            "product": self.product,
            "quantity": quantity,
            "unit_price": self.product.final_price,
            "line_total": self.product.final_price * quantity,
            "stock": self.product.stock_quantity,
        }])

    def _create(self, quantity=2, promo=None):
        return create_order(
            user=self.user, cart=self._cart(quantity),
            receiver_name="Nguyễn Văn A", receiver_phone="0900000000",
            shipping_address="1 Lê Lợi, Quận 1, TP.HCM", promo=promo,
        )

    def test_order_deducts_stock_and_stores_cogs(self):
        order = self._create(quantity=2)
        item = order.items.get()
        self.assertEqual(item.cost_price, Decimal(1000000))  # giá vốn lô A
        self.assertEqual(item.unit_price, Decimal(1500000))
        self.assertEqual(item.line_profit, Decimal(1000000))
        self.assertEqual(self.product.stock_quantity, 12)

    def test_cogs_is_weighted_average_across_batches(self):
        order = self._create(quantity=6)  # 4 từ lô A (1.000.000) + 2 từ lô B (1.200.000)
        item = order.items.get()
        expected = int((4 * 1000000 + 2 * 1200000) / 6)
        self.assertEqual(item.cost_price, Decimal(expected))
        self.assertEqual(item.batch_allocations.count(), 2)

    def test_order_creates_initial_status_history(self):
        order = self._create()
        history = order.status_history.get()
        self.assertEqual(history.from_status, "")
        self.assertEqual(history.to_status, Order.Status.PENDING)

    def test_order_code_is_generated(self):
        order = self._create()
        self.assertTrue(order.code.startswith("DH"))

    def test_free_shipping_threshold(self):
        order = self._create(quantity=2)  # 3.000.000đ > ngưỡng 2.000.000đ
        self.assertEqual(order.shipping_fee, 0)

    def test_promo_code_reduces_total(self):
        promo = PromoCode.objects.create(
            code="TEST10", discount_type=PromoCode.DiscountType.PERCENT, value=10,
            end_date=timezone.now() + timedelta(days=10),
        )
        order = self._create(quantity=2, promo=promo)
        self.assertEqual(order.discount_amount, Decimal(300000))
        self.assertEqual(order.total, Decimal(2700000))
        promo.refresh_from_db()
        self.assertEqual(promo.used_count, 1)

    def test_cancel_returns_stock_to_original_batches(self):
        order = self._create(quantity=6)
        self.assertEqual(self.product.stock_quantity, 8)

        cancel_order(order, user=self.user, reason="Đổi ý")

        self.batch_a.refresh_from_db()
        self.batch_b.refresh_from_db()
        self.assertEqual(self.batch_a.quantity_remaining, 4)   # hoàn đúng lô A
        self.assertEqual(self.batch_b.quantity_remaining, 10)  # hoàn đúng lô B
        self.assertEqual(order.status, Order.Status.CANCELLED)
        self.assertIsNotNone(order.cancelled_at)

    def test_cancel_is_idempotent_on_stock(self):
        order = self._create(quantity=3)
        cancel_order(order, user=self.user)
        with self.assertRaises(OrderError):
            cancel_order(order, user=self.user)
        self.assertEqual(self.product.stock_quantity, 14)  # không hoàn kho hai lần

    def test_cannot_cancel_while_shipping(self):
        order = self._create()
        change_order_status(order, Order.Status.CONFIRMED)
        change_order_status(order, Order.Status.SHIPPING)
        self.assertFalse(order.can_cancel)
        with self.assertRaises(OrderError):
            cancel_order(order, user=self.user)

    def test_status_changes_are_logged(self):
        order = self._create()
        change_order_status(order, Order.Status.CONFIRMED)
        change_order_status(order, Order.Status.SHIPPING)
        change_order_status(order, Order.Status.COMPLETED)
        self.assertEqual(
            list(order.status_history.values_list("to_status", flat=True)),
            ["pending", "confirmed", "shipping", "completed"],
        )
        self.assertIsNotNone(order.completed_at)

    def test_out_of_stock_raises_order_error(self):
        with self.assertRaises(OrderError):
            self._create(quantity=999)
        self.assertEqual(Order.objects.count(), 0)

    def test_order_profit_calculation(self):
        order = self._create(quantity=2)
        # Doanh thu 3.000.000 - giá vốn 2.000.000 = 1.000.000
        self.assertEqual(order.profit, Decimal(1000000))
