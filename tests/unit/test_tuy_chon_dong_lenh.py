"""Kiểm thử tuỳ chọn ``--tat-ca`` khai báo ở ``conftest.py`` gốc.

Vì sao đáng test: ``--tat-ca`` can thiệp trực tiếp vào ``config.option.markexpr``.
Nếu can thiệp sai, pytest vẫn chạy bình thường và **không báo lỗi gì** — chỉ có
điều nó chạy nhầm tập test. Loại lỗi im lặng như vậy chỉ có test mới bắt được.
"""
from types import SimpleNamespace

import pytest

from conftest import _nguoi_dung_tu_dat_marker

pytestmark = pytest.mark.unit


def _config_gia(*args):
    """Dựng một đối tượng giống ``pytest.Config`` vừa đủ cho hàm đang test."""
    return SimpleNamespace(invocation_params=SimpleNamespace(args=tuple(args)))


class TestNhanBietNguoiDungTuDatMarker:
    def test_khong_go_m_thi_tra_ve_false(self):
        assert _nguoi_dung_tu_dat_marker(_config_gia("--tat-ca")) is False

    def test_khong_co_tham_so_nao_cung_tra_ve_false(self):
        assert _nguoi_dung_tu_dat_marker(_config_gia()) is False

    def test_go_m_tach_roi_thi_tra_ve_true(self):
        assert _nguoi_dung_tu_dat_marker(_config_gia("--tat-ca", "-m", "e2e")) is True

    def test_go_m_dinh_lien_dau_bang_thi_tra_ve_true(self):
        assert _nguoi_dung_tu_dat_marker(_config_gia("-m=e2e")) is True

    def test_khong_nham_voi_tham_so_khac_bat_dau_bang_m(self):
        """``-maxfail`` không tồn tại, nhưng ``-m`` là tiền tố của nhiều thứ.

        Quan trọng là không được nhầm đường dẫn tệp hay tuỳ chọn khác thành
        bộ lọc marker.
        """
        assert _nguoi_dung_tu_dat_marker(_config_gia("tests/unit/test_models.py")) is False
        assert _nguoi_dung_tu_dat_marker(_config_gia("--markers")) is False


class TestTatCaTonTrongMarkerNguoiDungGo:
    """Kiểm tra hành vi thật của ``pytest_configure``, không chỉ hàm phụ trợ."""

    def _chay_configure(self, tat_ca, markexpr, *args):
        from conftest import pytest_configure

        config = SimpleNamespace(
            invocation_params=SimpleNamespace(args=tuple(args)),
            option=SimpleNamespace(markexpr=markexpr),
            getoption=lambda ten: tat_ca if ten == "--tat-ca" else None,
        )
        pytest_configure(config)
        return config.option.markexpr

    def test_tat_ca_xoa_bo_loc_mac_dinh(self):
        assert self._chay_configure(True, "not e2e", "--tat-ca") == ""

    def test_tat_ca_khong_nuot_marker_nguoi_dung_go(self):
        """``--tat-ca -m e2e`` phải chạy 45 ca E2E, không phải cả 351 ca."""
        assert self._chay_configure(True, "e2e", "--tat-ca", "-m", "e2e") == "e2e"

    def test_khong_co_tat_ca_thi_giu_nguyen_bo_loc(self):
        assert self._chay_configure(False, "not e2e") == "not e2e"
