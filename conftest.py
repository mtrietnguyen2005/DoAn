

def pytest_addoption(parser):
    parser.addoption(
        "--tat-ca",
        action="store_true",
        default=False,
        help="Chạy TẤT CẢ test, kể cả E2E (bỏ qua bộ lọc -m mặc định trong pytest.ini).",
    )


def _nguoi_dung_tu_dat_marker(config) -> bool:

    args = list(config.invocation_params.args)
    return any(a == "-m" or a.startswith("-m=") or a.startswith("--markers=") for a in args)


def pytest_configure(config):

    if config.getoption("--tat-ca") and not _nguoi_dung_tu_dat_marker(config):
        config.option.markexpr = ""
