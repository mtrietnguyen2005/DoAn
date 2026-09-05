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


def pytest_configure(config):
    """Xoá bộ lọc marker khi người dùng yêu cầu chạy tất cả.

    Lý do có tuỳ chọn này thay vì bảo người dùng gõ ``-m ""``: PowerShell bỏ
    luôn tham số là chuỗi rỗng khi gọi chương trình ngoài, nên pytest chỉ nhận
    được ``-m`` trơ trọi và báo lỗi "expected one argument".
    """
    if config.getoption("--tat-ca"):
        config.option.markexpr = ""
