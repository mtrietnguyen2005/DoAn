from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import Address, User

INPUT_CLASS = (
    "w-full rounded-lg border border-slate-300 px-4 py-2.5 text-sm "
    "focus:border-blue-500 focus:ring-2 focus:ring-blue-100 outline-none transition"
)


class TailwindMixin:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, (forms.CheckboxInput, forms.FileInput, forms.ClearableFileInput)):
                continue
            existing = widget.attrs.get("class", "")
            widget.attrs["class"] = f"{existing} {INPUT_CLASS}".strip()


class RegisterForm(TailwindMixin, UserCreationForm):
    email = forms.EmailField(label="Email", required=True)
    phone = forms.CharField(label="Số điện thoại", max_length=20, required=False)

    class Meta:
        model = User
        fields = ("username", "last_name", "first_name", "email", "phone")
        labels = {"username": "Tên đăng nhập", "last_name": "Họ", "first_name": "Tên"}

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Email này đã được sử dụng.")
        return email


class LoginForm(TailwindMixin, AuthenticationForm):
    username = forms.CharField(label="Tên đăng nhập hoặc Email")
    remember_me = forms.BooleanField(label="Ghi nhớ đăng nhập", required=False, initial=True)

    error_messages = {
        "invalid_login": "Tên đăng nhập/email hoặc mật khẩu không đúng.",
        "inactive": "Tài khoản này đã bị khóa.",
    }


class ProfileForm(TailwindMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ("last_name", "first_name", "email", "phone", "date_of_birth", "gender", "avatar")
        labels = {"last_name": "Họ", "first_name": "Tên"}
        widgets = {"date_of_birth": forms.DateInput(attrs={"type": "date"})}

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Email này đã được sử dụng bởi tài khoản khác.")
        return email


class AddressForm(TailwindMixin, forms.ModelForm):
    class Meta:
        model = Address
        fields = ("full_name", "phone", "province", "district", "ward", "street", "note", "is_default")
