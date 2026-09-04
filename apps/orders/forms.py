from django import forms

from apps.accounts.forms import TailwindMixin

from .models import Order


class CheckoutForm(TailwindMixin, forms.Form):
    receiver_name = forms.CharField(label="Họ tên người nhận", max_length=120)
    receiver_phone = forms.CharField(label="Số điện thoại", max_length=20)
    receiver_email = forms.EmailField(label="Email", required=False)
    province = forms.CharField(label="Tỉnh/Thành phố", max_length=100)
    district = forms.CharField(label="Quận/Huyện", max_length=100)
    ward = forms.CharField(label="Phường/Xã", max_length=100)
    street = forms.CharField(label="Địa chỉ cụ thể", max_length=255)
    customer_note = forms.CharField(
        label="Ghi chú đơn hàng", required=False,
        widget=forms.Textarea(attrs={"rows": 3, "placeholder": "Ví dụ: giao giờ hành chính..."}),
    )
    payment_method = forms.ChoiceField(
        label="Hình thức thanh toán",
        choices=Order.PaymentMethod.choices,
        initial=Order.PaymentMethod.COD,
        widget=forms.RadioSelect,
    )

    def clean_receiver_phone(self):
        phone = self.cleaned_data["receiver_phone"].strip()
        digits = phone.replace(" ", "").replace(".", "").replace("-", "")
        if not digits.isdigit() or not (9 <= len(digits) <= 11):
            raise forms.ValidationError("Số điện thoại không hợp lệ.")
        return digits

    @property
    def full_address(self):
        d = self.cleaned_data
        return f"{d['street']}, {d['ward']}, {d['district']}, {d['province']}"


class CancelOrderForm(TailwindMixin, forms.Form):
    reason = forms.CharField(
        label="Lý do hủy đơn", required=False, max_length=255,
        widget=forms.Textarea(attrs={"rows": 2, "placeholder": "Cho shop biết lý do bạn hủy đơn (không bắt buộc)"}),
    )
