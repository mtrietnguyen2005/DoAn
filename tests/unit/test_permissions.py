import pytest
from django.contrib import admin as django_admin

from apps.accounts.models import Address
from apps.catalog.models import Product, Review
from apps.core.admin_mixins import ReadOnlyForStaffMixin
from apps.inventory.models import Batch, StockTransaction

pytestmark = pytest.mark.django_db

READ_ONLY_MODELS = [Address, Review, StockTransaction]
EDITABLE_MODELS = [Product, Batch]


def admin_for(model):
    return django_admin.site._registry[model]


class FakeRequest:

    def __init__(self, user):
        self.user = user


@pytest.mark.unit
@pytest.mark.accounts
class TestReadOnlyResources:

    def test_quyen_han_cua_admin_thuong(self, staff_user):
        model_admin = admin_for(Address)
        request = FakeRequest(staff_user)
        assert model_admin.has_view_permission(request) is True
        assert model_admin.has_add_permission(request) is False
        assert model_admin.has_change_permission(request) is False
        assert model_admin.has_delete_permission(request) is False

    def test_moi_truong_deu_bi_khoa_voi_admin_thuong(self, staff_user):
        model_admin = admin_for(Address)
        readonly = model_admin.get_readonly_fields(FakeRequest(staff_user))
        ten_truong = {f.name for f in Address._meta.fields}
        assert ten_truong.issubset(set(readonly))

    @pytest.mark.parametrize("model", READ_ONLY_MODELS, ids=lambda m: m.__name__)
    def test_ca_ba_model_deu_dung_mixin_chi_doc(self, model, staff_user):
        model_admin = admin_for(model)
        assert isinstance(model_admin, ReadOnlyForStaffMixin)
        assert model_admin.has_add_permission(FakeRequest(staff_user)) is False


@pytest.mark.unit
@pytest.mark.accounts
class TestSuperuserFullAccess:

    @pytest.mark.parametrize("model", READ_ONLY_MODELS, ids=lambda m: m.__name__)
    def test_superuser_duoc_them_sua_xoa(self, model, superuser):
        model_admin = admin_for(model)
        request = FakeRequest(superuser)
        assert model_admin.has_add_permission(request) is True
        assert model_admin.has_change_permission(request) is True
        assert model_admin.has_delete_permission(request) is True

    @pytest.mark.parametrize("model", READ_ONLY_MODELS, ids=lambda m: m.__name__)
    def test_superuser_khong_bi_khoa_truong(self, model, superuser):
        readonly = admin_for(model).get_readonly_fields(FakeRequest(superuser))
        ten_truong = {f.name for f in model._meta.fields}
        assert not ten_truong.issubset(set(readonly))


@pytest.mark.unit
@pytest.mark.accounts
class TestEditableResourcesUnaffected:

    @pytest.mark.parametrize("model", EDITABLE_MODELS, ids=lambda m: m.__name__)
    def test_admin_thuong_van_sua_duoc_san_pham_va_lo_hang(self, model, staff_user):
        model_admin = admin_for(model)
        request = FakeRequest(staff_user)
        assert model_admin.has_add_permission(request) is True
        assert model_admin.has_change_permission(request) is True


@pytest.mark.unit
@pytest.mark.accounts
class TestReadOnlyViaHttp:

    def test_admin_thuong_xem_duoc_nhung_khong_them_duoc_qua_http(self, client, staff_user):
        client.force_login(staff_user)
        url = "/admin/accounts/address/"
        assert client.get(url).status_code == 200
        assert client.get(url + "add/").status_code == 403

    def test_admin_thuong_khong_sua_duoc_danh_gia_qua_http(self, client, staff_user, review):
        client.force_login(staff_user)
        response = client.post(
            f"/admin/catalog/review/{review.pk}/change/",
            {"rating": 1, "content": "Sửa trộm"},
        )
        assert response.status_code == 403
        review.refresh_from_db()
        assert review.rating == 5

    def test_superuser_vao_duoc_trang_them_moi_qua_http(self, client, superuser):
        client.force_login(superuser)
        assert client.get("/admin/accounts/address/add/").status_code == 200

    def test_admin_thuong_van_them_duoc_san_pham(self, client, staff_user):
        client.force_login(staff_user)
        assert client.get("/admin/catalog/product/add/").status_code == 200
