from decimal import Decimal

import pytest
from django.utils import timezone

from apps.inventory.models import Batch, StockTransaction
from apps.inventory.services import (
    OutOfStockError, adjust_batch, allocate_stock, receive_batch, return_stock,
)
from apps.orders.models import Order, OrderItemBatch, OrderStatusHistory, Shipping
from apps.orders.services import (
    OrderError, calculate_shipping_fee, cancel_order, change_order_status,
    create_order, restore_stock,
)

pytestmark = pytest.mark.django_db


@pytest.mark.unit
@pytest.mark.inventory
class TestAllocateStock:

    def test_uu_tien_lo_nhap_kho_som_nhat(self, product_with_batches, batch_early):
        allocations = allocate_stock(product_with_batches, 3, reference="TEST")

        assert len(allocations) == 1
        batch, quantity, cost = allocations[0]
        assert batch.pk == batch_early.pk
        assert quantity == 3
        assert cost == Decimal(1000000)

    def test_tru_dung_so_luong_tren_lo_duoc_chon(self, product_with_batches, batch_early, batch_late):
        allocate_stock(product_with_batches, 3, reference="TEST")

        batch_early.refresh_from_db()
        batch_late.refresh_from_db()
        assert batch_early.quantity_remaining == 1
        assert batch_late.quantity_remaining == 10
        assert product_with_batches.stock_quantity == 11

    def test_lay_tran_sang_lo_ke_tiep_khi_lo_dau_khong_du(self, product_with_batches, batch_early, batch_late):
        allocations = allocate_stock(product_with_batches, 6, reference="TEST")

        assert [(b.batch_code, q) for b, q, _ in allocations] == [("LO-SOM", 4), ("LO-MUON", 2)]
        batch_early.refresh_from_db()
        batch_late.refresh_from_db()
        assert batch_early.quantity_remaining == 0
        assert batch_late.quantity_remaining == 8

    def test_hai_lo_cung_ngay_nhap_xep_theo_id(self, product, batch_factory):
        lo_truoc = batch_factory(product, quantity=5, cost_price=900000,
                                 received_days_ago=7, batch_code="LO-A")
        lo_sau = batch_factory(product, quantity=5, cost_price=1100000,
                               received_days_ago=7, batch_code="LO-B")

        allocations = allocate_stock(product, 5, reference="TEST")
        assert allocations[0][0].pk == lo_truoc.pk
        lo_sau.refresh_from_db()
        assert lo_sau.quantity_remaining == 5

    def test_bao_loi_khi_ton_kho_khong_du(self, product_with_batches):
        with pytest.raises(OutOfStockError) as exc:
            allocate_stock(product_with_batches, 999)
        assert "không đủ" in str(exc.value)

    def test_khong_tru_kho_khi_xuat_that_bai(self, product_with_batches):
        ton_kho_truoc = product_with_batches.stock_quantity
        with pytest.raises(OutOfStockError):
            allocate_stock(product_with_batches, 999)
        assert product_with_batches.stock_quantity == ton_kho_truoc
        assert StockTransaction.objects.filter(
            transaction_type=StockTransaction.Type.OUT).count() == 0

    @pytest.mark.parametrize("so_luong_khong_hop_le", [0, -1, -100])
    def test_bao_loi_khi_so_luong_khong_duong(self, product_with_batches, so_luong_khong_hop_le):
        with pytest.raises(ValueError):
            allocate_stock(product_with_batches, so_luong_khong_hop_le)

    def test_lay_toan_bo_ton_kho_con_lai(self, product_with_batches):
        allocate_stock(product_with_batches, 14, reference="TEST")
        assert product_with_batches.stock_quantity == 0


@pytest.mark.unit
@pytest.mark.inventory
class TestStockTransactionLog:

    def test_ghi_vet_giao_dich_xuat_kho(self, product_with_batches, batch_early):
        allocate_stock(product_with_batches, 3, reference="DH001", note="Bán hàng")

        tx = StockTransaction.objects.get(reference="DH001")
        assert tx.transaction_type == StockTransaction.Type.OUT
        assert tx.quantity == -3
        assert tx.quantity_after == 1
        assert tx.batch_id == batch_early.pk
        assert tx.note == "Bán hàng"

    def test_moi_lo_sinh_mot_ban_ghi_giao_dich_rieng(self, product_with_batches):
        allocate_stock(product_with_batches, 6, reference="DH002")
        assert StockTransaction.objects.filter(reference="DH002").count() == 2

    def test_ghi_nhan_nguoi_thuc_hien(self, product_with_batches, superuser):
        allocate_stock(product_with_batches, 1, reference="DH003", user=superuser)
        assert StockTransaction.objects.get(reference="DH003").created_by == superuser

    def test_ghi_vet_nhap_kho(self, product, batch_factory, superuser):
        batch = batch_factory(product, quantity=20, cost_price=800000)
        receive_batch(batch, user=superuser)

        tx = StockTransaction.objects.get(transaction_type=StockTransaction.Type.IN)
        assert tx.quantity == 20
        assert tx.quantity_after == 20
        assert tx.created_by == superuser


@pytest.mark.unit
@pytest.mark.inventory
class TestReturnAndAdjustStock:

    def test_hoan_tra_ve_dung_lo_ban_dau(self, product_with_batches, batch_early, batch_late):
        allocate_stock(product_with_batches, 4, reference="DH004")
        batch_early.refresh_from_db()
        assert batch_early.quantity_remaining == 0

        return_stock(batch_early, 4, reference="DH004")

        batch_early.refresh_from_db()
        batch_late.refresh_from_db()
        assert batch_early.quantity_remaining == 4
        assert batch_late.quantity_remaining == 10

    def test_ghi_vet_giao_dich_hoan_tra(self, product_with_batches, batch_early):
        allocate_stock(product_with_batches, 2, reference="DH005")
        return_stock(batch_early, 2, reference="DH005")

        tx = StockTransaction.objects.get(
            reference="DH005", transaction_type=StockTransaction.Type.RETURN)
        assert tx.quantity == 2
        assert tx.quantity_after == 4

    def test_hoan_tra_so_luong_bang_khong_khong_lam_gi(self, batch_early):
        return_stock(batch_early, 0)
        assert StockTransaction.objects.count() == 0

    def test_dieu_chinh_giam_ton_kho(self, batch_late):
        adjust_batch(batch_late, 4, note="Kiểm kê phát hiện thiếu")

        batch_late.refresh_from_db()
        assert batch_late.quantity_remaining == 4
        tx = StockTransaction.objects.get(transaction_type=StockTransaction.Type.ADJUST)
        assert tx.quantity == -6
        assert tx.note == "Kiểm kê phát hiện thiếu"

    def test_dieu_chinh_tang_vuot_so_luong_nhap_thi_noi_rong_so_luong_nhap(self, batch_early):
        adjust_batch(batch_early, 10)

        batch_early.refresh_from_db()
        assert batch_early.quantity_remaining == 10
        assert batch_early.quantity_in == 10

    def test_dieu_chinh_khong_doi_thi_khong_ghi_giao_dich(self, batch_early):
        adjust_batch(batch_early, batch_early.quantity_remaining)
        assert StockTransaction.objects.count() == 0


@pytest.mark.unit
@pytest.mark.finance
class TestShippingFee:

    def test_don_nho_phai_tra_phi_ship(self, settings):
        assert calculate_shipping_fee(Decimal(1000000)) == Decimal(settings.DEFAULT_SHIPPING_FEE)

    def test_don_dat_nguong_duoc_mien_phi_ship(self, settings):
        assert calculate_shipping_fee(Decimal(settings.FREE_SHIPPING_THRESHOLD)) == Decimal(0)

    def test_don_vuot_nguong_duoc_mien_phi_ship(self, settings):
        assert calculate_shipping_fee(Decimal(settings.FREE_SHIPPING_THRESHOLD) + 1) == Decimal(0)

    def test_ngay_duoi_nguong_van_phai_tra_phi(self, settings):
        phi = calculate_shipping_fee(Decimal(settings.FREE_SHIPPING_THRESHOLD) - 1)
        assert phi == Decimal(settings.DEFAULT_SHIPPING_FEE)


@pytest.mark.unit
@pytest.mark.finance
class TestOrderCOGS:

    def test_luu_gia_von_cua_lo_duoc_xuat(self, product_with_batches, order_factory):
        order = order_factory(product_with_batches, quantity=2)

        item = order.items.get()
        assert item.cost_price == Decimal(1000000)
        assert item.unit_price == Decimal(1500000)
        assert item.line_profit == Decimal(1000000)

    def test_gia_von_la_binh_quan_gia_quyen_khi_lay_tu_nhieu_lo(self, product_with_batches, order_factory):
        order = order_factory(product_with_batches, quantity=6)

        item = order.items.get()
        ky_vong = int((4 * 1000000 + 2 * 1200000) / 6)
        assert item.cost_price == Decimal(ky_vong)
        assert item.batch_allocations.count() == 2

    def test_gia_von_khong_doi_khi_lo_moi_co_gia_khac(self, product_with_batches, order_factory, batch_factory):
        order = order_factory(product_with_batches, quantity=2)
        gia_von_luc_ban = order.items.get().cost_price

        batch_factory(product_with_batches, quantity=50, cost_price=2000000)

        order.items.get().refresh_from_db()
        assert order.items.get().cost_price == gia_von_luc_ban

    def test_luu_ban_sao_ten_va_ma_san_pham(self, product_with_batches, order_factory):
        item = order_factory(product_with_batches, quantity=1).items.get()
        assert item.product_name == product_with_batches.name
        assert item.product_sku == product_with_batches.sku

    def test_ghi_nhan_phan_bo_tung_lo(self, product_with_batches, order_factory, batch_early, batch_late):
        order = order_factory(product_with_batches, quantity=6)

        allocations = {a.batch_id: a for a in OrderItemBatch.objects.filter(order_item__order=order)}
        assert allocations[batch_early.pk].quantity == 4
        assert allocations[batch_early.pk].cost_price == Decimal(1000000)
        assert allocations[batch_late.pk].quantity == 2
        assert allocations[batch_late.pk].cost_price == Decimal(1200000)
        assert all(not a.is_returned for a in allocations.values())


@pytest.mark.unit
@pytest.mark.finance
class TestOrderTotalCalculation:

    def test_don_nho_cong_them_phi_ship(self, product_with_batches, order_factory, settings):
        order = order_factory(product_with_batches, quantity=1)

        assert order.subtotal == Decimal(1500000)
        assert order.shipping_fee == Decimal(settings.DEFAULT_SHIPPING_FEE)
        assert order.discount_amount == Decimal(0)
        assert order.total == Decimal(1500000) + Decimal(settings.DEFAULT_SHIPPING_FEE)

    def test_don_lon_duoc_mien_phi_ship(self, product_with_batches, order_factory):
        order = order_factory(product_with_batches, quantity=2)

        assert order.subtotal == Decimal(3000000)
        assert order.shipping_fee == Decimal(0)
        assert order.total == Decimal(3000000)

    def test_ap_dung_ma_giam_theo_phan_tram(self, product_with_batches, order_factory, promo_percent):
        order = order_factory(product_with_batches, quantity=2, promo=promo_percent)

        assert order.discount_amount == Decimal(300000)
        assert order.total == Decimal(2700000)
        assert order.promo_code == promo_percent

    def test_ma_giam_gia_tang_bo_dem_luot_su_dung(self, product_with_batches, order_factory, promo_percent):
        order_factory(product_with_batches, quantity=2, promo=promo_percent)
        promo_percent.refresh_from_db()
        assert promo_percent.used_count == 1

    def test_dat_hang_bang_gia_khuyen_mai_cua_san_pham(self, discounted_product, batch_factory, order_factory):
        batch_factory(discounted_product, quantity=5, cost_price=5000000)
        order = order_factory(discounted_product, quantity=1)

        assert order.items.get().unit_price == Decimal(7000000)
        assert order.subtotal == Decimal(7000000)

    def test_don_nhieu_dong_hang_cong_don_dung(self, product_with_batches, product_factory,
                                               batch_factory, cart_factory, customer):
        khac = product_factory(name="RAM 16GB", sku="RAM0001", price=Decimal(1000000))
        batch_factory(khac, quantity=10, cost_price=700000)

        order = create_order(
            user=customer,
            cart=cart_factory((product_with_batches, 2), (khac, 3)),
            receiver_name="A", receiver_phone="0900000000", shipping_address="x",
        )
        assert order.subtotal == Decimal(6000000)
        assert order.items.count() == 2
        assert order.total_quantity == 5


@pytest.mark.unit
class TestCreateOrder:
    def test_tru_kho_khi_dat_hang(self, product_with_batches, order_factory):
        order_factory(product_with_batches, quantity=3)
        assert product_with_batches.stock_quantity == 11

    def test_ghi_lich_su_trang_thai_ban_dau(self, order):
        history = order.status_history.get()
        assert history.from_status == ""
        assert history.to_status == Order.Status.PENDING
        assert history.note

    def test_don_moi_o_trang_thai_cho_xac_nhan(self, order):
        assert order.status == Order.Status.PENDING
        assert order.can_cancel is True

    def test_tu_dong_tao_ban_ghi_van_chuyen(self, order):
        assert Shipping.objects.filter(order=order).exists()
        assert order.shipping.fee == order.shipping_fee

    def test_xoa_gio_hang_sau_khi_dat_thanh_cong(self, product_with_batches, cart_factory, customer):
        cart = cart_factory((product_with_batches, 1))
        create_order(user=customer, cart=cart, receiver_name="A",
                     receiver_phone="0900000000", shipping_address="x")
        assert cart.cleared is True

    def test_bao_loi_khi_gio_hang_rong(self, cart_factory, customer):
        with pytest.raises(OrderError) as exc:
            create_order(user=customer, cart=cart_factory(), receiver_name="A",
                         receiver_phone="0900000000", shipping_address="x")
        assert "trống" in str(exc.value)

    def test_khong_tao_don_khi_khong_du_ton_kho(self, product_with_batches, cart_factory, customer):
        with pytest.raises(OrderError):
            create_order(user=customer, cart=cart_factory((product_with_batches, 999)),
                         receiver_name="A", receiver_phone="0900000000", shipping_address="x")

        assert Order.objects.count() == 0
        assert product_with_batches.stock_quantity == 14

    def test_luu_thong_tin_nguoi_nhan(self, product_with_batches, cart_factory, customer):
        order = create_order(
            user=customer, cart=cart_factory((product_with_batches, 1)),
            receiver_name="Trần Thị B", receiver_phone="0987654321",
            receiver_email="b@test.vn", shipping_address="99 Trần Hưng Đạo, Quận 5, TP.HCM",
            customer_note="Giao giờ hành chính",
        )
        assert order.receiver_name == "Trần Thị B"
        assert order.receiver_phone == "0987654321"
        assert order.customer_note == "Giao giờ hành chính"
        assert order.payment_method == Order.PaymentMethod.COD


@pytest.mark.unit
class TestChangeOrderStatus:
    def test_ghi_lich_su_moi_lan_doi_trang_thai(self, order, superuser):
        change_order_status(order, Order.Status.CONFIRMED, user=superuser)
        change_order_status(order, Order.Status.SHIPPING, user=superuser)
        change_order_status(order, Order.Status.COMPLETED, user=superuser)

        assert list(order.status_history.values_list("to_status", flat=True)) == [
            "pending", "confirmed", "shipping", "completed",
        ]
        assert order.status_history.last().changed_by == superuser

    def test_danh_dau_moc_thoi_gian_hoan_thanh(self, order):
        change_order_status(order, Order.Status.COMPLETED)
        assert order.completed_at is not None
        assert order.shipping.delivered_at is not None

    def test_danh_dau_moc_thoi_gian_ban_giao_van_chuyen(self, order):
        change_order_status(order, Order.Status.SHIPPING)
        assert order.shipping.shipped_at is not None

    def test_doi_sang_chinh_trang_thai_hien_tai_khong_ghi_lich_su(self, order):
        so_ban_ghi = order.status_history.count()
        change_order_status(order, order.status)
        assert order.status_history.count() == so_ban_ghi

    def test_khong_cho_doi_trang_thai_don_da_huy(self, order):
        change_order_status(order, Order.Status.CANCELLED)
        with pytest.raises(OrderError) as exc:
            change_order_status(order, Order.Status.CONFIRMED)
        assert "đã hủy" in str(exc.value)

    def test_khong_cho_doi_trang_thai_don_da_hoan_thanh(self, order):
        change_order_status(order, Order.Status.COMPLETED)
        with pytest.raises(OrderError):
            change_order_status(order, Order.Status.SHIPPING)

    def test_van_cho_phep_huy_don_da_hoan_thanh(self, order):
        change_order_status(order, Order.Status.COMPLETED)
        change_order_status(order, Order.Status.CANCELLED)
        assert order.status == Order.Status.CANCELLED

    def test_bao_loi_voi_trang_thai_khong_ton_tai(self, order):
        with pytest.raises(OrderError) as exc:
            change_order_status(order, "trang_thai_bia_dat")
        assert "không hợp lệ" in str(exc.value)


@pytest.mark.unit
@pytest.mark.inventory
class TestCancelOrderRestoresStock:

    def test_huy_don_hoan_lai_dung_tung_lo(self, product_with_batches, order_factory,
                                           batch_early, batch_late, customer):
        order = order_factory(product_with_batches, quantity=6)
        batch_early.refresh_from_db()
        batch_late.refresh_from_db()
        assert (batch_early.quantity_remaining, batch_late.quantity_remaining) == (0, 8)

        cancel_order(order, user=customer, reason="Đổi ý")

        batch_early.refresh_from_db()
        batch_late.refresh_from_db()
        assert batch_early.quantity_remaining == 4
        assert batch_late.quantity_remaining == 10
        assert product_with_batches.stock_quantity == 14

    def test_huy_don_ghi_vet_giao_dich_hoan_kho(self, order, customer):
        cancel_order(order, user=customer)

        tx = StockTransaction.objects.filter(
            reference=order.code, transaction_type=StockTransaction.Type.RETURN)
        assert tx.count() == 1
        assert tx.first().quantity == 2

    def test_danh_dau_da_hoan_de_khong_hoan_hai_lan(self, order, customer):
        cancel_order(order, user=customer)
        assert all(a.is_returned for a in OrderItemBatch.objects.filter(order_item__order=order))

    def test_goi_hoan_kho_lan_hai_khong_lam_tang_ton_kho(self, product_with_batches, order, customer):
        cancel_order(order, user=customer)
        ton_kho = product_with_batches.stock_quantity

        restore_stock(order, user=customer)
        assert product_with_batches.stock_quantity == ton_kho

    def test_huy_don_hoan_lai_luot_dung_ma_giam_gia(self, product_with_batches, order_factory,
                                                    promo_percent, customer):
        order = order_factory(product_with_batches, quantity=2, promo=promo_percent)
        promo_percent.refresh_from_db()
        assert promo_percent.used_count == 1

        cancel_order(order, user=customer)

        promo_percent.refresh_from_db()
        assert promo_percent.used_count == 0

    def test_khong_cho_huy_don_dang_giao(self, order, customer):
        change_order_status(order, Order.Status.CONFIRMED)
        change_order_status(order, Order.Status.SHIPPING)

        with pytest.raises(OrderError) as exc:
            cancel_order(order, user=customer)
        assert "không thể hủy" in str(exc.value)

    def test_ton_kho_khong_doi_khi_huy_don_that_bai(self, product_with_batches, order, customer):
        change_order_status(order, Order.Status.SHIPPING)
        ton_kho = product_with_batches.stock_quantity

        with pytest.raises(OrderError):
            cancel_order(order, user=customer)
        assert product_with_batches.stock_quantity == ton_kho

    def test_khong_the_huy_don_hai_lan(self, order, customer):
        cancel_order(order, user=customer)
        with pytest.raises(OrderError):
            cancel_order(order, user=customer)

    def test_huy_don_ghi_lai_ly_do(self, order, customer):
        cancel_order(order, user=customer, reason="Tìm được chỗ rẻ hơn")
        assert "Tìm được chỗ rẻ hơn" in order.status_history.last().note

    def test_danh_dau_moc_thoi_gian_huy(self, order, customer):
        cancel_order(order, user=customer)
        assert order.cancelled_at is not None
