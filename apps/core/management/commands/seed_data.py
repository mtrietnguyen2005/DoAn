"""Tạo dữ liệu mẫu để chạy thử website: python manage.py seed_data"""
import random
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.catalog.models import Brand, Category, Product, Review, Supplier
from apps.content.models import Banner, News, Promotion
from apps.inventory.models import Batch
from apps.inventory.services import receive_batch
from apps.orders.models import PromoCode

User = get_user_model()

CATEGORIES = [
    ("CPU - Bộ vi xử lý", "🔲"), ("VGA - Card đồ họa", "🎮"), ("RAM - Bộ nhớ trong", "📇"),
    ("Mainboard - Bo mạch chủ", "🧩"), ("Ổ cứng SSD/HDD", "💾"), ("PSU - Nguồn máy tính", "🔌"),
    ("Case & Tản nhiệt", "🖥️"), ("Màn hình", "🖵"), ("Laptop", "💻"), ("Phụ kiện", "⌨️"),
]

BRANDS = [
    ("Intel", "Hoa Kỳ"), ("AMD", "Hoa Kỳ"), ("NVIDIA", "Hoa Kỳ"), ("ASUS", "Đài Loan"),
    ("MSI", "Đài Loan"), ("Gigabyte", "Đài Loan"), ("Kingston", "Hoa Kỳ"), ("Corsair", "Hoa Kỳ"),
    ("Samsung", "Hàn Quốc"), ("Western Digital", "Hoa Kỳ"), ("Dell", "Hoa Kỳ"), ("Logitech", "Thụy Sĩ"),
]

SUPPLIERS = [
    ("Công ty TNHH Phân phối Máy tính Sài Gòn", "Nguyễn Văn An", "0283822111"),
    ("Công ty CP Công nghệ Viễn Sơn", "Trần Thị Bình", "0243756222"),
    ("Nhà phân phối Hà Nội Computer", "Lê Minh Cường", "0243999333"),
    ("Công ty TNHH Digiworld", "Phạm Thu Dung", "0287300444"),
]

PRODUCTS = [
    # (danh mục, thương hiệu, tên, giá, giá KM, mô tả ngắn, thông số)
    (0, 0, "Intel Core i5-13400F (10 nhân / 16 luồng, 2.5GHz - 4.6GHz)", 4290000, 3990000,
     "CPU 10 nhân 16 luồng, hiệu năng gaming xuất sắc trong tầm giá.",
     "Socket: LGA 1700\nSố nhân: 10 (6P + 4E)\nSố luồng: 16\nXung nhịp: 2.5GHz - 4.6GHz\nCache: 20MB\nTDP: 65W"),
    (0, 0, "Intel Core i7-13700K (16 nhân / 24 luồng, 3.4GHz - 5.4GHz)", 10490000, None,
     "CPU cao cấp cho game thủ và người sáng tạo nội dung.",
     "Socket: LGA 1700\nSố nhân: 16 (8P + 8E)\nSố luồng: 24\nXung nhịp: 3.4GHz - 5.4GHz\nCache: 30MB\nTDP: 125W"),
    (0, 1, "AMD Ryzen 5 7600X (6 nhân / 12 luồng, 4.7GHz - 5.3GHz)", 5990000, 5490000,
     "Vi xử lý AM5 thế hệ mới, tối ưu cho gaming.",
     "Socket: AM5\nSố nhân: 6\nSố luồng: 12\nXung nhịp: 4.7GHz - 5.3GHz\nCache: 38MB\nTDP: 105W"),
    (0, 1, "AMD Ryzen 7 7800X3D (8 nhân / 16 luồng, 3D V-Cache)", 11990000, None,
     "CPU gaming mạnh nhất nhờ công nghệ 3D V-Cache.",
     "Socket: AM5\nSố nhân: 8\nSố luồng: 16\nXung nhịp: 4.2GHz - 5.0GHz\nCache: 104MB\nTDP: 120W"),
    (1, 3, "ASUS Dual GeForce RTX 4060 OC 8GB GDDR6", 8590000, 7990000,
     "Card đồ họa RTX 4060 8GB, chơi mượt game AAA ở Full HD.",
     "GPU: GeForce RTX 4060\nBộ nhớ: 8GB GDDR6\nGiao tiếp: PCIe 4.0 x8\nCổng xuất: 3x DP, 1x HDMI\nNguồn đề nghị: 550W"),
    (1, 4, "MSI Gaming X GeForce RTX 4070 SUPER 12GB", 18990000, None,
     "Hiệu năng 2K mạnh mẽ với tản nhiệt TRI FROZR 3.",
     "GPU: GeForce RTX 4070 SUPER\nBộ nhớ: 12GB GDDR6X\nGiao tiếp: PCIe 4.0 x16\nCổng xuất: 3x DP, 1x HDMI\nNguồn đề nghị: 700W"),
    (1, 5, "Gigabyte Radeon RX 7600 GAMING OC 8GB", 6790000, 6290000,
     "Card AMD tầm trung, hiệu năng/giá tốt cho Full HD.",
     "GPU: Radeon RX 7600\nBộ nhớ: 8GB GDDR6\nGiao tiếp: PCIe 4.0 x8\nNguồn đề nghị: 550W"),
    (2, 6, "Kingston Fury Beast 16GB (2x8GB) DDR5 5200MHz", 1590000, 1390000,
     "Kit RAM DDR5 hiệu năng cao, tản nhiệt nhôm.",
     "Dung lượng: 16GB (2x8GB)\nLoại: DDR5\nBus: 5200MHz\nCL: 40\nĐiện áp: 1.25V"),
    (2, 7, "Corsair Vengeance RGB 32GB (2x16GB) DDR5 6000MHz", 3290000, None,
     "RAM DDR5 32GB đèn RGB, tối ưu cho nền tảng AMD EXPO.",
     "Dung lượng: 32GB (2x16GB)\nLoại: DDR5\nBus: 6000MHz\nCL: 36\nĐiện áp: 1.35V"),
    (3, 3, "ASUS TUF Gaming B760M-PLUS WIFI DDR5", 4590000, 4290000,
     "Mainboard mATX bền bỉ chuẩn quân đội, có WiFi 6.",
     "Socket: LGA 1700\nChipset: B760\nKích thước: mATX\nRAM: 4x DDR5 tối đa 128GB\nKết nối: WiFi 6, 2.5Gb LAN"),
    (3, 5, "Gigabyte B650M DS3H (AM5, DDR5)", 3390000, None,
     "Bo mạch chủ AM5 giá tốt cho Ryzen 7000 series.",
     "Socket: AM5\nChipset: B650\nKích thước: mATX\nRAM: 4x DDR5 tối đa 128GB\nM.2: 2 khe PCIe 4.0"),
    (4, 8, "SSD Samsung 990 PRO 1TB NVMe PCIe Gen4 M.2", 3190000, 2890000,
     "Ổ SSD NVMe Gen4 tốc độ đọc lên tới 7450MB/s.",
     "Dung lượng: 1TB\nChuẩn: M.2 NVMe PCIe 4.0\nTốc độ đọc: 7450 MB/s\nTốc độ ghi: 6900 MB/s\nBảo hành: 60 tháng"),
    (4, 9, "HDD Western Digital Blue 2TB 7200RPM SATA3", 1690000, None,
     "Ổ cứng lưu trữ dung lượng lớn, hoạt động ổn định.",
     "Dung lượng: 2TB\nChuẩn: SATA 3 6Gb/s\nTốc độ quay: 7200 RPM\nBộ nhớ đệm: 256MB"),
    (5, 7, "Nguồn Corsair RM750e 750W 80 Plus Gold Full Modular", 2690000, 2490000,
     "PSU 750W chuẩn 80 Plus Gold, dây modular toàn phần.",
     "Công suất: 750W\nChuẩn: 80 Plus Gold\nModular: Full\nQuạt: 120mm\nBảo hành: 84 tháng"),
    (6, 4, "Tản nhiệt nước MSI MAG CORELIQUID 240R V2", 2290000, None,
     "Tản nhiệt AIO 240mm với đèn ARGB đồng bộ.",
     "Kích thước: 240mm\nQuạt: 2x 120mm ARGB\nHỗ trợ socket: LGA 1700, AM5, AM4"),
    (7, 3, "Màn hình ASUS TUF Gaming VG249Q1A 24\" IPS 165Hz", 3490000, 3190000,
     "Màn hình gaming 24 inch, 165Hz, tấm nền IPS.",
     "Kích thước: 24 inch\nĐộ phân giải: 1920x1080\nTần số quét: 165Hz\nTấm nền: IPS\nThời gian phản hồi: 1ms MPRT"),
    (7, 8, "Màn hình Samsung Odyssey G5 27\" QHD 165Hz cong", 5990000, None,
     "Màn hình cong 1000R chuẩn QHD dành cho game thủ.",
     "Kích thước: 27 inch\nĐộ phân giải: 2560x1440\nTần số quét: 165Hz\nĐộ cong: 1000R"),
    (8, 3, "Laptop ASUS TUF Gaming F15 (i5-12500H, RTX 3050, 16GB, 512GB)", 21990000, 19990000,
     "Laptop gaming hiệu năng cao, màn hình 144Hz.",
     "CPU: Intel Core i5-12500H\nRAM: 16GB DDR4\nỔ cứng: 512GB SSD NVMe\nVGA: RTX 3050 4GB\nMàn hình: 15.6\" FHD 144Hz"),
    (8, 10, "Laptop Dell Inspiron 15 3520 (i5-1235U, 16GB, 512GB)", 15990000, 14990000,
     "Laptop văn phòng mỏng nhẹ, pin bền.",
     "CPU: Intel Core i5-1235U\nRAM: 16GB DDR4\nỔ cứng: 512GB SSD\nMàn hình: 15.6\" FHD 120Hz"),
    (9, 11, "Chuột không dây Logitech G304 Lightspeed", 790000, 690000,
     "Chuột gaming không dây độ trễ thấp, pin 250 giờ.",
     "Kết nối: Lightspeed 2.4GHz\nCảm biến: HERO 12000 DPI\nTrọng lượng: 99g\nPin: 250 giờ"),
]

NEWS_POSTS = [
    ("Hướng dẫn chọn CPU phù hợp cho từng nhu cầu năm 2025",
     "Chọn CPU không chỉ nhìn vào số nhân. Bài viết giúp bạn chọn đúng vi xử lý theo nhu cầu và ngân sách.",
     "cpu, tư vấn, build pc"),
    ("So sánh RTX 4060 và RX 7600: đâu là lựa chọn tốt hơn?",
     "Hai card đồ họa tầm trung phổ biến nhất hiện nay được đặt lên bàn cân về hiệu năng, điện năng và giá bán.",
     "vga, so sánh, gaming"),
    ("DDR5 đã đủ rẻ để nâng cấp chưa?",
     "Giá RAM DDR5 đã giảm mạnh. Đây là thời điểm thích hợp để chuyển đổi nền tảng?",
     "ram, ddr5, nâng cấp"),
    ("5 lỗi thường gặp khi tự ráp máy tính lần đầu",
     "Những sai lầm phổ biến khiến máy không lên nguồn và cách xử lý nhanh chóng.",
     "build pc, mẹo hay"),
]


class Command(BaseCommand):
    help = "Tạo dữ liệu mẫu (danh mục, thương hiệu, sản phẩm, lô hàng, tin tức, khuyến mãi...)"

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true", help="Xóa dữ liệu mẫu cũ trước khi tạo mới")

    @transaction.atomic
    def handle(self, *args, **options):
        random.seed(2025)

        if options["reset"]:
            self.stdout.write("Đang xóa dữ liệu cũ...")
            Product.objects.all().delete()
            Category.objects.all().delete()
            Brand.objects.all().delete()
            Supplier.objects.all().delete()
            News.objects.all().delete()
            Promotion.objects.all().delete()
            Banner.objects.all().delete()
            PromoCode.objects.all().delete()

        # --- Tài khoản ---
        admin, created = User.objects.get_or_create(
            username="admin",
            defaults={"email": "admin@linhkienpc.vn", "is_staff": True, "is_superuser": True,
                      "last_name": "Quản", "first_name": "Trị"},
        )
        if created:
            admin.set_password("admin123456")
            admin.save()
            self.stdout.write(self.style.SUCCESS("  ✓ Tài khoản quản trị: admin / admin123456"))

        customers = []
        for i in range(1, 6):
            user, created = User.objects.get_or_create(
                username=f"khachhang{i}",
                defaults={"email": f"khachhang{i}@example.com", "last_name": "Nguyễn", "first_name": f"Khách {i}",
                          "phone": f"09{random.randint(10000000, 99999999)}"},
            )
            if created:
                user.set_password("khachhang123")
                user.save()
            customers.append(user)
        self.stdout.write(self.style.SUCCESS("  ✓ 5 tài khoản khách hàng: khachhang1..5 / khachhang123"))

        # --- Danh mục, thương hiệu, nhà cung cấp ---
        categories = [
            Category.objects.get_or_create(name=name, defaults={"icon": icon, "display_order": index})[0]
            for index, (name, icon) in enumerate(CATEGORIES)
        ]
        brands = [
            Brand.objects.get_or_create(name=name, defaults={"country": country})[0]
            for name, country in BRANDS
        ]
        suppliers = [
            Supplier.objects.get_or_create(
                name=name,
                defaults={"contact_person": contact, "phone": phone,
                          "email": f"sales{index}@ncc.vn", "address": "TP. Hồ Chí Minh",
                          "description": "Nhà phân phối linh kiện máy tính chính hãng."},
            )[0]
            for index, (name, contact, phone) in enumerate(SUPPLIERS)
        ]
        self.stdout.write(self.style.SUCCESS(
            f"  ✓ {len(categories)} danh mục, {len(brands)} thương hiệu, {len(suppliers)} nhà cung cấp"))

        # --- Sản phẩm + lô hàng ---
        today = timezone.localdate()
        created_products = []
        for index, (cat_index, brand_index, name, price, sale, short, specs) in enumerate(PRODUCTS, start=1):
            product, created = Product.objects.get_or_create(
                sku=f"SP{index:04d}",
                defaults={
                    "name": name,
                    "category": categories[cat_index],
                    "brand": brands[brand_index],
                    "supplier": random.choice(suppliers),
                    "short_description": short,
                    "description": f"{short}\n\nSản phẩm chính hãng, đầy đủ hộp và phụ kiện, bảo hành tại các trung tâm ủy quyền trên toàn quốc.",
                    "specifications": specs,
                    "price": Decimal(price),
                    "sale_price": Decimal(sale) if sale else None,
                    "warranty_months": random.choice([12, 24, 36]),
                    "is_featured": index % 3 == 0,
                },
            )
            created_products.append(product)

            if created:
                for batch_index in range(random.randint(1, 2)):
                    quantity = random.randint(5, 40)
                    batch = Batch.objects.create(
                        product=product,
                        batch_code=f"LO{index:04d}{batch_index + 1}",
                        supplier=product.supplier,
                        quantity_in=quantity,
                        quantity_remaining=quantity,
                        cost_price=Decimal(int(price * random.uniform(0.72, 0.85))),
                        received_date=today - timedelta(days=random.randint(1, 120)),
                        note="Lô hàng nhập mẫu",
                    )
                    receive_batch(batch, user=admin, note=f"Nhập lô {batch.batch_code}")
        self.stdout.write(self.style.SUCCESS(f"  ✓ {len(created_products)} sản phẩm kèm lô hàng"))

        # --- Đánh giá ---
        review_count = 0
        for product in created_products:
            for user in random.sample(customers, random.randint(0, 3)):
                _, created = Review.objects.get_or_create(
                    product=product, user=user,
                    defaults={
                        "rating": random.randint(3, 5),
                        "title": random.choice(["Rất hài lòng", "Sản phẩm tốt", "Đáng đồng tiền", "Giao hàng nhanh"]),
                        "content": random.choice([
                            "Hàng chính hãng, đóng gói cẩn thận, chạy rất ổn định.",
                            "Shop tư vấn nhiệt tình, sản phẩm đúng mô tả, sẽ ủng hộ tiếp.",
                            "Hiệu năng tốt so với tầm giá, nhiệt độ mát.",
                            "Giao hàng nhanh, lắp vào máy chạy ngon.",
                        ]),
                    },
                )
                review_count += int(created)
        self.stdout.write(self.style.SUCCESS(f"  ✓ {review_count} đánh giá"))

        # --- Tin tức ---
        for title, summary, tags in NEWS_POSTS:
            News.objects.get_or_create(
                title=title,
                defaults={
                    "summary": summary, "tags": tags, "author": admin,
                    "content": f"{summary}\n\nĐây là nội dung bài viết mẫu dùng để minh họa giao diện trang tin tức của website. "
                               f"Bạn có thể chỉnh sửa nội dung này trong trang quản trị tại mục Tin tức.",
                    "published_at": timezone.now() - timedelta(days=random.randint(1, 30)),
                },
            )
        self.stdout.write(self.style.SUCCESS(f"  ✓ {len(NEWS_POSTS)} bài tin tức"))

        # --- Khuyến mãi & mã giảm giá ---
        promotion, created = Promotion.objects.get_or_create(
            title="Đại tiệc linh kiện – Giảm đến 20%",
            defaults={
                "description": "Chương trình khuyến mãi cuối tháng dành cho CPU, VGA và RAM. Số lượng có hạn!",
                "discount_percent": 20,
                "start_date": timezone.now() - timedelta(days=2),
                "end_date": timezone.now() + timedelta(days=20),
            },
        )
        if created:
            promotion.products.set([p for p in created_products if p.sale_price][:8])

        PromoCode.objects.get_or_create(
            code="CHAOBAN",
            defaults={"description": "Giảm 5% cho đơn hàng đầu tiên", "discount_type": PromoCode.DiscountType.PERCENT,
                      "value": 5, "max_discount": 500000, "min_order_value": 500000,
                      "end_date": timezone.now() + timedelta(days=90), "usage_limit": 0},
        )
        PromoCode.objects.get_or_create(
            code="GIAM200K",
            defaults={"description": "Giảm 200.000đ cho đơn từ 5 triệu", "discount_type": PromoCode.DiscountType.FIXED,
                      "value": 200000, "min_order_value": 5000000,
                      "end_date": timezone.now() + timedelta(days=60), "usage_limit": 100},
        )
        self.stdout.write(self.style.SUCCESS("  ✓ 1 chương trình khuyến mãi, 2 mã giảm giá (CHAOBAN, GIAM200K)"))

        self.stdout.write(self.style.SUCCESS("\n✅ Đã tạo xong dữ liệu mẫu!"))
        self.stdout.write("   Đăng nhập quản trị: http://127.0.0.1:8000/admin/  (admin / admin123456)")
