"""Kiểm thử nghiệp vụ kho: phân bổ FIFO, hoàn kho đúng lô, điều chỉnh thủ công."""
from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from apps.catalog.models import Brand, Category, Product
from apps.inventory.models import Batch, StockTransaction
from apps.inventory.services import OutOfStockError, adjust_batch, allocate_stock, return_stock


class InventoryServiceTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="CPU")
        self.brand = Brand.objects.create(name="Intel")
        self.product = Product.objects.create(
            name="Intel Core i5", sku="TEST001", category=self.category, brand=self.brand, price=5000000
        )
        today = timezone.localdate()
        # Lô A hết hạn sớm hơn -> phải được xuất trước
        self.batch_a = Batch.objects.create(
            product=self.product, batch_code="A", quantity_in=5, quantity_remaining=5,
            cost_price=Decimal(4000000), expiry_date=today + timedelta(days=10),
        )
        self.batch_b = Batch.objects.create(
            product=self.product, batch_code="B", quantity_in=10, quantity_remaining=10,
            cost_price=Decimal(4200000), expiry_date=today + timedelta(days=100),
        )

    def test_stock_quantity_is_sum_of_batches(self):
        self.assertEqual(self.product.stock_quantity, 15)

    def test_allocate_uses_earliest_expiry_first(self):
        allocations = allocate_stock(self.product, 3, reference="TEST")
        self.assertEqual(len(allocations), 1)
        self.assertEqual(allocations[0][0].batch_code, "A")
        self.batch_a.refresh_from_db()
        self.assertEqual(self.batch_a.quantity_remaining, 2)

    def test_allocate_spans_multiple_batches(self):
        allocations = allocate_stock(self.product, 8, reference="TEST")
        self.assertEqual([(b.batch_code, q) for b, q, _ in allocations], [("A", 5), ("B", 3)])
        self.assertEqual(self.product.stock_quantity, 7)

    def test_allocate_raises_when_not_enough_stock(self):
        with self.assertRaises(OutOfStockError):
            allocate_stock(self.product, 999)
        self.assertEqual(self.product.stock_quantity, 15)  # không trừ kho khi lỗi

    def test_allocate_writes_transaction_log(self):
        allocate_stock(self.product, 2, reference="DH001")
        tx = StockTransaction.objects.get(reference="DH001")
        self.assertEqual(tx.transaction_type, StockTransaction.Type.OUT)
        self.assertEqual(tx.quantity, -2)
        self.assertEqual(tx.quantity_after, 3)

    def test_return_stock_goes_back_to_original_batch(self):
        allocate_stock(self.product, 5, reference="DH002")
        self.batch_a.refresh_from_db()
        self.assertEqual(self.batch_a.quantity_remaining, 0)

        return_stock(self.batch_a, 5, reference="DH002")
        self.batch_a.refresh_from_db()
        self.batch_b.refresh_from_db()
        self.assertEqual(self.batch_a.quantity_remaining, 5)
        self.assertEqual(self.batch_b.quantity_remaining, 10)
        self.assertTrue(StockTransaction.objects.filter(
            reference="DH002", transaction_type=StockTransaction.Type.RETURN).exists())

    def test_adjust_batch_records_delta(self):
        adjust_batch(self.batch_b, 4, note="Kiểm kê")
        self.batch_b.refresh_from_db()
        self.assertEqual(self.batch_b.quantity_remaining, 4)
        tx = StockTransaction.objects.filter(transaction_type=StockTransaction.Type.ADJUST).first()
        self.assertEqual(tx.quantity, -6)
