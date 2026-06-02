from django import forms
from django.forms import inlineformset_factory
from PIL import Image

from .models import Order, OrderItem, Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "article",
            "name",
            "unit",
            "price",
            "supplier",
            "manufacturer",
            "category",
            "discount",
            "quantity",
            "description",
            "photo",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }

    def clean_price(self):
        price = self.cleaned_data["price"]
        if price < 0:
            raise forms.ValidationError("Цена не может быть отрицательной.")
        return price

    def clean_discount(self):
        discount = self.cleaned_data["discount"]
        if discount < 0 or discount > 100:
            raise forms.ValidationError("Скидка должна быть от 0 до 100.")
        return discount

    def clean_photo(self):
        photo = self.cleaned_data.get("photo")
        if not photo:
            return photo
        try:
            image = Image.open(photo)
            image.verify()
        except Exception as exc:
            raise forms.ValidationError("Загрузите корректное изображение.") from exc
        photo.seek(0)
        return photo


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            "order_date",
            "delivery_date",
            "pickup_point",
            "status",
        ]
        widgets = {
            "order_date": forms.DateInput(attrs={"type": "date"}),
            "delivery_date": forms.DateInput(attrs={"type": "date"}),
        }

class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ["product", "count"]

    def clean_count(self):
        count = self.cleaned_data["count"]
        if count <= 0:
            raise forms.ValidationError("Количество должно быть больше нуля.")
        return count


OrderItemFormSet = inlineformset_factory(
    Order,
    OrderItem,
    form=OrderItemForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True,
)
