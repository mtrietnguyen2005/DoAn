"""Tuỳ chọn dòng lệnh dùng chung cho toàn bộ bộ kiểm thử.

Đặt ở thư mục gốc vì pytest chỉ nhận ``pytest_addoption`` từ conftest gốc.
"""


def pytest_addoption(parser):
    parser.addoption(
        "--tat-ca",
        action="store_true",
        default=False,
        help="Chạy TẤT CẢ test, kể cả E2E (bỏ qua bộ lọc -m mặc định trong pytest.ini).",
    )


def _nguoi_dung_tu_dat_marker(config) -> bool:
    """Người dùng có tự gõ ``-m ...`` trên dòng lệnh hay không?

    ``config.option.markexpr`` không phân biệt được bộ lọc đến từ đâu, vì
    ``addopts`` trong pytest.ini được ghép vào y như thể gõ tay. Nên phải soi
    đúng những gì người dùng thật sự gõ.
    """
    args = list(config.invocation_params.args)
    return any(a == "-m" or a.startswith("-m=") or a.startswith("--markers=") for a in args)


def pytest_configure(config):
    """Xoá bộ lọc marker khi người dùng yêu cầu chạy tất cả.

    Lý do có tuỳ chọn này thay vì bảo người dùng gõ ``-m ""``: PowerShell bỏ
    luôn tham số là chuỗi rỗng khi gọi chương trình ngoài, nên pytest chỉ nhận
    được ``-m`` trơ trọi và báo lỗi "expected one argument".

    Nhưng nếu người dùng ĐÃ tự gõ ``-m`` (ví dụ ``--tat-ca -m e2e`` để chạy
    riêng phần E2E) thì phải tôn trọng bộ lọc đó. Nếu không, ``--tat-ca`` sẽ
    âm thầm nuốt mất ``-m e2e`` và chạy cả 351 test trong khi người dùng chỉ
    chờ 45 ca — sai mà không hề báo lỗi.
    """
    if config.getoption("--tat-ca") and not _nguoi_dung_tu_dat_marker(config):
        config.option.markexpr = ""
