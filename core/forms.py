from django import forms
from django.forms import inlineformset_factory
from PIL import Image

from .models import Order, OrderItem, Product


class PhotoClearableFileInput(forms.ClearableFileInput):
    # Стандартный виджет Django выводит checkbox перед текстом, а в макете нужен обратный порядок.
    template_name = "core/widgets/clearable_file_input.html"


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
            "price": forms.NumberInput(attrs={"min": "0", "step": "0.01"}),
            "discount": forms.NumberInput(attrs={"min": "0", "max": "100", "step": "0.01"}),
            "quantity": forms.NumberInput(attrs={"min": "0"}),
            "photo": PhotoClearableFileInput(),
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
            width, height = image.size
            image.verify()
        except Exception as exc:
            raise forms.ValidationError("Загрузите корректное изображение.") from exc

        if width > 300 or height > 200:
            raise forms.ValidationError(
                "Размер изображения не должен превышать 300x200 пикселей."
            )

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

    def clean(self):
        cleaned_data = super().clean()
        order_date = cleaned_data.get("order_date")
        delivery_date = cleaned_data.get("delivery_date")

        # Заказ не может быть доставлен в день оформления или раньше него.
        if order_date and delivery_date and order_date >= delivery_date:
            raise forms.ValidationError(
                "Дата заказа должна быть раньше даты доставки."
            )

        return cleaned_data


class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ["product", "count"]
        widgets = {
            "count": forms.NumberInput(attrs={"min": "1"}),
        }

    def clean_count(self):
        count = self.cleaned_data["count"]
        if count <= 0:
            raise forms.ValidationError("Количество должно быть больше нуля.")
        return count


OrderItemFormSet = inlineformset_factory(
    Order,
    OrderItem,
    form=OrderItemForm,
    extra=2,
    can_delete=True,
    min_num=1,
    # В макете и выданных данных у заказа предусмотрено не больше двух товарных позиций.
    max_num=2,
    validate_min=True,
    validate_max=True,
)
