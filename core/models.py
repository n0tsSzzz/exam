from decimal import Decimal

from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.Model):
    ADMIN = "admin"
    MANAGER = "manager"
    CLIENT = "client"

    ROLE_CHOICES = [
        (ADMIN, "Администратор"),
        (MANAGER, "Менеджер"),
        (CLIENT, "Клиент"),
    ]

    name = models.CharField("Роль", max_length=30, choices=ROLE_CHOICES, unique=True)

    class Meta:
        verbose_name = "роль"
        verbose_name_plural = "роли"
        ordering = ["name"]

    def __str__(self):
        return self.get_name_display()


class User(AbstractUser):
    full_name = models.CharField("ФИО", max_length=255)
    role = models.ForeignKey(
        Role,
        verbose_name="Роль",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "пользователь"
        verbose_name_plural = "пользователи"

class NamedModel(models.Model):
    name = models.CharField("Название", max_length=200, unique=True)

    class Meta:
        abstract = True
        ordering = ["name"]

    def __str__(self):
        return self.name


class Supplier(NamedModel):
    class Meta(NamedModel.Meta):
        verbose_name = "поставщик"
        verbose_name_plural = "поставщики"


class Category(NamedModel):
    class Meta(NamedModel.Meta):
        verbose_name = "категория"
        verbose_name_plural = "категории"


class Manufacturer(NamedModel):
    class Meta(NamedModel.Meta):
        verbose_name = "производитель"
        verbose_name_plural = "производители"


class PickupPoint(models.Model):
    address = models.TextField("Адрес", unique=True)

    class Meta:
        verbose_name = "пункт выдачи"
        verbose_name_plural = "пункты выдачи"
        ordering = ["address"]

    def __str__(self):
        return self.address


class Product(models.Model):
    article = models.CharField("Артикул", max_length=50, unique=True)
    name = models.CharField("Название", max_length=255)
    unit = models.CharField("Единица измерения", max_length=20, default="шт.")
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2)
    supplier = models.ForeignKey(Supplier, verbose_name="Поставщик", on_delete=models.PROTECT)
    manufacturer = models.ForeignKey(
        Manufacturer,
        verbose_name="Производитель",
        on_delete=models.PROTECT,
    )
    category = models.ForeignKey(Category, verbose_name="Категория", on_delete=models.PROTECT)
    discount = models.DecimalField("Скидка, %", max_digits=5, decimal_places=2, default=0)
    quantity = models.PositiveIntegerField("Количество на складе", default=0)
    description = models.TextField("Описание", blank=True)
    photo = models.ImageField("Фото", upload_to="products/", null=True, blank=True)

    class Meta:
        verbose_name = "товар"
        verbose_name_plural = "товары"
        ordering = ["article"]

    def __str__(self):
        return f"{self.article} - {self.name}"

    @property
    def final_price(self):
        price = Decimal(str(self.price))
        discount = Decimal(str(self.discount or 0))
        if not discount:
            return price
        return price * (Decimal("1") - discount / Decimal("100"))

    def save(self, *args, **kwargs):
        old_photo = None
        if self.pk:
            old_photo = Product.objects.filter(pk=self.pk).values_list("photo", flat=True).first()
        super().save(*args, **kwargs)
        if old_photo and self.photo and old_photo != self.photo.name:
            # При замене изображения старый файл больше не используется и должен быть удален.
            self.photo.storage.delete(old_photo)

    def delete(self, *args, **kwargs):
        photo_name = self.photo.name if self.photo else None
        storage = self.photo.storage if self.photo else None
        result = super().delete(*args, **kwargs)
        if photo_name and storage:
            storage.delete(photo_name)
        return result

class Order(models.Model):
    STATUS_NEW = "new"
    STATUS_DONE = "done"

    STATUS_CHOICES = [
        (STATUS_NEW, "Новый"),
        (STATUS_DONE, "Завершен"),
    ]

    order_date = models.DateField("Дата заказа")
    delivery_date = models.DateField("Дата доставки")
    pickup_point = models.ForeignKey(
        PickupPoint,
        verbose_name="Пункт выдачи",
        on_delete=models.PROTECT,
    )
    client = models.ForeignKey(
        User,
        verbose_name="Клиент",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
    )
    client_name = models.CharField("ФИО клиента", max_length=255, blank=True)
    pickup_code = models.PositiveIntegerField("Код получения", default=0)
    status = models.CharField(
        "Статус",
        max_length=30,
        choices=STATUS_CHOICES,
        default=STATUS_NEW,
    )

    class Meta:
        verbose_name = "заказ"
        verbose_name_plural = "заказы"
        ordering = ["-order_date", "-id"]

    def __str__(self):
        return f"Заказ #{self.pk}"

    @property
    def articles_summary(self):
        # Макет заказа требует вывести пары "артикул, количество" в одной строке.
        items = self.items.select_related("product")
        return ", ".join(f"{item.product.article}, {item.count}" for item in items)

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.select_related("product"))


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        verbose_name="Заказ",
        related_name="items",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(Product, verbose_name="Товар", on_delete=models.PROTECT)
    count = models.PositiveIntegerField("Количество", default=1)

    class Meta:
        verbose_name = "позиция заказа"
        verbose_name_plural = "позиции заказа"

    def __str__(self):
        return f"{self.product} x {self.count}"

    @property
    def total_price(self):
        return self.product.final_price * self.count
