from datetime import timedelta
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import identify_hasher
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.accounts.models import Address
from apps.catalog.models import Product, Review
from apps.inventory.models import Batch
from apps.orders.models import Order, OrderItem, PromoCode

User = get_user_model()

pytestmark = pytest.mark.django_db


@pytest.mark.unit
@pytest.mark.inventory
class TestProductStock:

    def test_san_pham_chua_co_lo_thi_ton_kho_bang_0(self, product):
        assert product.stock_quantity == 0
        assert product.in_stock is False

    def test_ton_kho_cong_don_tu_nhieu_lo(self, product, batch_early, batch_late):
        assert product.stock_quantity == 14
        assert product.in_stock is True

    def test_ton_kho_cap_nhat_khi_lo_thay_doi(self, product, batch_early):
        assert product.stock_quantity == 4
        batch_early.quantity_remaining = 1
        batch_early.save()
        assert product.stock_quantity == 1

    def test_lo_het_hang_khong_con_tinh_vao_ton_kho(self, product, batch_early, batch_late):
        batch_early.quantity_remaining = 0
        batch_early.save()
        assert product.stock_quantity == 10

    def test_them_lo_moi_lam_tang_ton_kho(self, product, batch_early, batch_factory):
        batch_factory(product, quantity=25, cost_price=900000)
        assert product.stock_quantity == 29


@pytest.mark.unit
@pytest.mark.inventory
class TestBatchModel:

    def test_so_luong_da_ban(self, batch_early):
        batch_early.quantity_remaining = 1
        assert batch_early.quantity_sold == 3

    def test_tong_gia_von_cua_lo(self, batch_early):
        assert batch_early.total_cost == Decimal(4000000)

    def test_ngay_nhap_kho_mac_dinh_la_hom_nay(self, product, batch_factory, today):
        batch = batch_factory(product)
        assert batch.received_date == today

    def test_thu_tu_mac_dinh_theo_ngay_nhap_kho(self, product, batch_early, batch_late):
        ma_lo = list(product.batches.values_list("batch_code", flat=True))
        assert ma_lo == ["LO-SOM", "LO-MUON"]

    def test_khong_cho_so_luong_con_lai_lon_hon_so_luong_nhap(self, product):
        batch = Batch(product=product, batch_code="LOI01", quantity_in=5,
                      quantity_remaining=10, cost_price=Decimal(1000))
        with pytest.raises(ValidationError) as exc:
            batch.full_clean()
        assert "quantity_remaining" in exc.value.message_dict

    def test_khong_cho_ngay_san_xuat_sau_ngay_nhap_kho(self, product, today):
        batch = Batch(
            product=product, batch_code="LOI02", quantity_in=5, quantity_remaining=5,
            cost_price=Decimal(1000),
            received_date=today, manufacture_date=today + timedelta(days=1),
        )
        with pytest.raises(ValidationError) as exc:
            batch.full_clean()
        assert "manufacture_date" in exc.value.message_dict

    def test_ma_lo_phai_la_duy_nhat(self, product, batch_early):
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                Batch.objects.create(
                    product=product, batch_code=batch_early.batch_code,
                    quantity_in=1, quantity_remaining=1, cost_price=Decimal(1000),
                )


@pytest.mark.unit
@pytest.mark.finance
class TestProductPricing:

    def test_khong_khuyen_mai_thi_gia_ban_la_gia_goc(self, product):
        assert product.final_price == Decimal(1500000)
        assert product.has_discount is False
        assert product.discount_percent == 0

    def test_co_khuyen_mai_thi_uu_tien_gia_khuyen_mai(self, discounted_product):
        assert discounted_product.final_price == Decimal(7000000)
        assert discounted_product.has_discount is True

    def test_phan_tram_giam_lam_tron_xuong(self, discounted_product):
        assert discounted_product.discount_percent == 12

    def test_bo_qua_gia_khuyen_mai_cao_hon_gia_goc(self, product_factory):
        product = product_factory(price=Decimal(1000000), sale_price=Decimal(1200000))
        assert product.final_price == Decimal(1000000)
        assert product.has_discount is False
        assert product.discount_percent == 0

    def test_gia_khuyen_mai_bang_gia_goc_khong_tinh_la_giam(self, product_factory):
        product = product_factory(price=Decimal(1000000), sale_price=Decimal(1000000))
        assert product.has_discount is False


@pytest.mark.unit
@pytest.mark.finance
class TestPromoCode:

    def test_ma_giam_theo_phan_tram(self, promo_percent):
        assert promo_percent.calculate_discount(Decimal(1000000)) == Decimal(100000)

    def test_ma_giam_phan_tram_bi_chan_boi_muc_giam_toi_da(self, promo_percent):
        assert promo_percent.calculate_discount(Decimal(10000000)) == Decimal(500000)

    def test_ma_giam_so_tien_co_dinh(self, promo_fixed):
        assert promo_fixed.calculate_discount(Decimal(6000000)) == Decimal(200000)

    def test_so_tien_giam_khong_vuot_qua_gia_tri_don(self, db):
        promo = PromoCode.objects.create(
            code="GIAMLON", discount_type=PromoCode.DiscountType.FIXED,
            value=Decimal(500000), end_date=timezone.now() + timedelta(days=1),
        )
        assert promo.calculate_discount(Decimal(100000)) == Decimal(100000)

    def test_ma_duoc_chuyen_thanh_chu_hoa(self, db):
        promo = PromoCode.objects.create(
            code="  giamgia10  ", discount_type=PromoCode.DiscountType.PERCENT,
            value=Decimal(10), end_date=timezone.now() + timedelta(days=1),
        )
        assert promo.code == "GIAMGIA10"

    def test_ma_hop_le_khong_bao_loi(self, promo_percent):
        assert promo_percent.error_for(Decimal(1000000)) is None
        assert promo_percent.is_available is True

    def test_bao_loi_khi_ma_het_han(self, promo_expired):
        assert "hết hạn" in promo_expired.error_for(Decimal(1000000))
        assert promo_expired.is_available is False

    def test_bao_loi_khi_chua_du_gia_tri_don_toi_thieu(self, promo_fixed):
        error = promo_fixed.error_for(Decimal(1000000))
        assert error is not None and "tối thiểu" in error

    def test_bao_loi_khi_ma_bi_vo_hieu_hoa(self, promo_percent):
        promo_percent.is_active = False
        assert "vô hiệu hóa" in promo_percent.error_for(Decimal(1000000))

    def test_bao_loi_khi_het_luot_su_dung(self, promo_percent):
        promo_percent.usage_limit = 5
        promo_percent.used_count = 5
        assert "hết lượt" in promo_percent.error_for(Decimal(1000000))
        assert promo_percent.is_available is False

    def test_gioi_han_bang_0_nghia_la_khong_gioi_han(self, promo_percent):
        promo_percent.usage_limit = 0
        promo_percent.used_count = 9999
        assert promo_percent.is_available is True


@pytest.mark.unit
@pytest.mark.finance
class TestOrderTotals:

    def test_tong_tien_bang_tam_tinh_cong_ship_tru_giam(self, db):
        order = Order.objects.create(
            receiver_name="A", receiver_phone="0900000000", shipping_address="x",
            subtotal=Decimal(1000000), shipping_fee=Decimal(30000),
            discount_amount=Decimal(100000),
            total=Decimal(1000000) + Decimal(30000) - Decimal(100000),
        )
        assert order.total == Decimal(930000)

    def test_gia_von_va_loi_nhuan_cua_tung_dong_hang(self, db, product):
        order = Order.objects.create(
            receiver_name="A", receiver_phone="0900000000", shipping_address="x",
            subtotal=Decimal(3000000), total=Decimal(3000000),
        )
        item = OrderItem.objects.create(
            order=order, product=product, product_name=product.name,
            unit_price=Decimal(1500000), cost_price=Decimal(1000000), quantity=2,
        )
        assert item.line_total == Decimal(3000000)
        assert item.line_cost == Decimal(2000000)
        assert item.line_profit == Decimal(1000000)

    def test_tong_gia_von_va_loi_nhuan_cua_ca_don(self, db, product, product_factory):
        order = Order.objects.create(
            receiver_name="A", receiver_phone="0900000000", shipping_address="x",
            subtotal=Decimal(4000000), discount_amount=Decimal(200000),
            total=Decimal(3800000),
        )
        OrderItem.objects.create(order=order, product=product, product_name="A",
                                 unit_price=Decimal(1500000), cost_price=Decimal(1000000), quantity=2)
        OrderItem.objects.create(order=order, product=product_factory(), product_name="B",
                                 unit_price=Decimal(1000000), cost_price=Decimal(700000), quantity=1)
        assert order.total_cost == Decimal(2700000)
        assert order.total_quantity == 3
        assert order.profit == Decimal(4000000) - Decimal(2700000) - Decimal(200000)

    def test_ma_don_hang_duoc_sinh_tu_dong(self, db):
        order = Order.objects.create(
            receiver_name="A", receiver_phone="0900000000", shipping_address="x",
        )
        assert order.code.startswith("DH")
        assert str(order.pk).zfill(5) in order.code


@pytest.mark.unit
class TestOrderStatus:

    @pytest.mark.parametrize("status,cho_phep_huy", [
        (Order.Status.PENDING, True),
        (Order.Status.CONFIRMED, True),
        (Order.Status.SHIPPING, False),
        (Order.Status.COMPLETED, False),
        (Order.Status.CANCELLED, False),
    ])
    def test_quyen_huy_don_theo_tung_trang_thai(self, db, status, cho_phep_huy):
        order = Order.objects.create(
            receiver_name="A", receiver_phone="0900000000",
            shipping_address="x", status=status,
        )
        assert order.can_cancel is cho_phep_huy


@pytest.mark.unit
@pytest.mark.accounts
class TestUserModel:

    def test_mat_khau_khong_bao_gio_luu_dang_van_ban_tho(self, customer):
        assert customer.password != "MatKhauManh!23"
        assert customer.check_password("MatKhauManh!23") is True
        assert customer.check_password("mat-khau-sai") is False

    def test_mat_khau_duoc_bam_bang_thuat_toan_hop_le(self, customer):
        assert identify_hasher(customer.password) is not None

    def test_cau_hinh_production_dung_pbkdf2(self, settings, db):
        from django.conf import global_settings

        settings.PASSWORD_HASHERS = global_settings.PASSWORD_HASHERS
        user = User.objects.create_user(
            username="kiemtrabam", email="bam@test.vn", password="MatKhauManh!23"
        )
        assert user.password.startswith("pbkdf2_sha256$")

    def test_email_phai_la_duy_nhat(self, customer, db):
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                User.objects.create_user(
                    username="trungemail", email=customer.email, password="MatKhauManh!23"
                )

    def test_ten_hien_thi_uu_tien_ho_ten_day_du(self, user_factory):
        user = user_factory(username="nguyenvana", last_name="Nguyễn", first_name="An")
        assert user.display_name == "Nguyễn An"

    def test_ten_hien_thi_lui_ve_ten_dang_nhap_khi_chua_co_ho_ten(self, customer):
        assert customer.display_name == "khachhang"

    def test_superuser_co_day_du_co_quyen(self, superuser):
        assert superuser.is_staff is True
        assert superuser.is_superuser is True


@pytest.mark.unit
@pytest.mark.accounts
class TestAddressModel:

    def test_dia_chi_dau_tien_tu_dong_thanh_mac_dinh(self, address):
        address.refresh_from_db()
        assert address.is_default is True

    def test_chi_ton_tai_duy_nhat_mot_dia_chi_mac_dinh(self, customer, address):
        moi = Address.objects.create(
            user=customer, full_name="Người B", phone="0911111111",
            province="Hà Nội", district="Ba Đình", ward="Cống Vị",
            street="1 Đội Cấn", is_default=True,
        )
        address.refresh_from_db()
        assert moi.is_default is True
        assert address.is_default is False
        assert Address.objects.filter(user=customer, is_default=True).count() == 1

    def test_dia_chi_cua_hai_nguoi_dung_khong_anh_huong_nhau(self, customer, other_customer, address):
        khac = Address.objects.create(
            user=other_customer, full_name="Người khác", phone="0922222222",
            province="Đà Nẵng", district="Hải Châu", ward="Thanh Bình", street="5 Bạch Đằng",
        )
        address.refresh_from_db()
        assert address.is_default is True
        assert khac.is_default is True

    def test_ghep_dia_chi_day_du(self, address):
        assert address.full_address == "12 Lê Lợi, Bến Nghé, Quận 1, TP.HCM"

    def test_thuoc_tinh_dia_chi_mac_dinh_cua_user(self, customer, address):
        assert customer.default_address == address


@pytest.mark.unit
class TestProductMisc:
    def test_slug_duoc_sinh_tu_dong_tu_ten(self, product):
        assert product.slug == "intel-core-i5-13400f"

    def test_slug_trung_ten_duoc_them_hau_to_so(self, product, product_factory):
        khac = product_factory(name=product.name, sku="CPU0002")
        assert khac.slug == "intel-core-i5-13400f-2"

    def test_tach_thong_so_ky_thuat_thanh_cap_ten_gia_tri(self, product):
        assert product.spec_lines == [
            ("Socket", "LGA 1700"), ("Số nhân", "10"), ("TDP", "65W"),
        ]

    def test_thong_so_rong_tra_ve_danh_sach_rong(self, product_factory):
        assert product_factory(specifications="").spec_lines == []


@pytest.mark.unit
class TestReviewModel:
    def test_diem_danh_gia_trung_binh(self, product, customer, other_customer):
        Review.objects.create(product=product, user=customer, rating=5, content="Tốt")
        Review.objects.create(product=product, user=other_customer, rating=4, content="Khá")
        assert product.rating_average == 4.5
        assert product.rating_count == 2

    def test_san_pham_chua_co_danh_gia(self, product):
        assert product.rating_average == 0
        assert product.rating_count == 0

    def test_moi_nguoi_chi_danh_gia_mot_san_pham_mot_lan(self, product, customer, review):
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                Review.objects.create(product=product, user=customer, rating=1, content="Lần hai")
