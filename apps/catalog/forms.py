from django import forms

from apps.accounts.forms import TailwindMixin

from .models import Review


class ReviewForm(TailwindMixin, forms.ModelForm):
    rating = forms.TypedChoiceField(
        label="Đánh giá",
        choices=[(i, f"{i} sao") for i in range(5, 0, -1)],
        coerce=int,
        initial=5,
    )

    class Meta:
        model = Review
        fields = ("rating", "title", "content")
        widgets = {
            "content": forms.Textarea(attrs={"rows": 4, "placeholder": "Chia sẻ trải nghiệm của bạn về sản phẩm..."}),
            "title": forms.TextInput(attrs={"placeholder": "Tiêu đề đánh giá (không bắt buộc)"}),
        }
