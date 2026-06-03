import csv
import os
from datetime import datetime
from typing import Any

from django.core.management.color import no_style
from django.core.management.base import BaseCommand
from django.db import connection

from core.models import (
    Category,
    Manufacturer,
    Order,
    OrderItem,
    PickupPoint,
    Product,
    Role,
    Supplier,
    User,
)


ROLE_MAP = {
    "администратор": Role.ADMIN,
    "admin": Role.ADMIN,
    "менеджер": Role.MANAGER,
    "manager": Role.MANAGER,
    "клиент": Role.CLIENT,
    "client": Role.CLIENT,
}

STATUS_MAP = {
    "новый": Order.STATUS_NEW,
    "new": Order.STATUS_NEW,
    "завершен": Order.STATUS_DONE,
    "выдан": Order.STATUS_DONE,
    "done": Order.STATUS_DONE,
}


class Command(BaseCommand):
    help = "Импортирует данные из CSV-файлов."

    def add_arguments(self, parser):
        parser.add_argument(
            "--path",
            default="import_data",
            help="Папка с CSV-файлами. По умолчанию import_data.",
        )

    def handle(self, *args: Any, **options: Any) -> str | None:
        base_path = options["path"]

        self.create_roles()
        self.import_pickup_points(base_path)
        self.import_products(base_path)
        self.import_users(base_path)
        self.import_orders(base_path)
        # В CSV заказы приходят с готовыми ID, поэтому sequence нужно сдвинуть после импорта.
        self.reset_sequences()

        self.stdout.write(self.style.SUCCESS("Импорт CSV завершен."))
        return None

    def create_roles(self):
        for role_name, _role_title in Role.ROLE_CHOICES:
            Role.objects.get_or_create(name=role_name)

    def import_pickup_points(self, base_path):
        path = self.first_file(base_path, "pp.csv", "pickup_points.csv", "Пункты выдачи_import.csv")
        if not path:
            self.stdout.write(self.style.WARNING("Файл пунктов выдачи не найден."))
            return

        with open(path, encoding="utf-8-sig", newline="") as file:
            reader = csv.reader(file, delimiter=";")
            for row in reader:
                print(row)
                if not row:
                    continue

                address = row[0].strip()
                if self.key(address) in ("address", "адрес"):
                    continue

                if address:
                    PickupPoint.objects.get_or_create(address=address)

    def import_products(self, base_path):
        path = self.first_file(base_path, "products.csv", "tovar.csv", "Tovar.csv")
        if not path:
            self.stdout.write(self.style.WARNING("Файл товаров не найден."))
            return

        with open(path, encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file, delimiter=self.get_delimiter(file))
            for row in reader:
                print(row)
                article = self.value(row, "article", "артикул")
                if not article:
                    continue

                supplier, _ = Supplier.objects.get_or_create(
                    name=self.value(row, "supplier", "поставщик") or "Не указан"
                )
                manufacturer, _ = Manufacturer.objects.get_or_create(
                    name=self.value(row, "manufacturer", "производитель") or "Не указан"
                )
                category, _ = Category.objects.get_or_create(
                    name=self.value(row, "category", "категория", "категория товара") or "Не указано"
                )

                photo = self.value(row, "photo", "фото")
                if photo and not photo.startswith("products/"):
                    # В базе хранится путь относительно MEDIA_ROOT, а в CSV указан только файл.
                    photo = f"products/{photo}"

                Product.objects.update_or_create(
                    article=article,
                    defaults={
                        "name": self.value(row, "name", "наименование товара", "название"),
                        "unit": self.value(row, "unit", "единица измерения") or "шт.",
                        "price": self.decimal(self.value(row, "price", "цена")),
                        "supplier": supplier,
                        "manufacturer": manufacturer,
                        "category": category,
                        "discount": self.decimal(
                            self.value(row, "discount", "действующая скидка", "скидка")
                        ),
                        "quantity": self.integer(
                            self.value(row, "quantity", "кол-во на складе", "количество")
                        ),
                        "description": self.value(row, "description", "описание товара", "описание"),
                        "photo": photo,
                    },
                )

    def import_users(self, base_path):
        path = self.first_file(base_path, "users.csv", "user_import.csv")
        if not path:
            self.stdout.write(self.style.WARNING("Файл пользователей не найден."))
            return

        with open(path, encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file, delimiter=self.get_delimiter(file))
            for row in reader:
                print(row)
                login = self.value(row, "login", "логин", "email")
                password = self.value(row, "password", "пароль")
                full_name = self.value(row, "full_name", "фио") or login
                role_name = self.value(row, "role", "роль", "роль сотрудника").lower()
                role_value = ROLE_MAP.get(role_name, Role.CLIENT)

                if not login or not password:
                    continue

                role, _ = Role.objects.get_or_create(name=role_value)
                user, created = User.objects.get_or_create(
                    username=login,
                    defaults={
                        "full_name": full_name,
                        "email": login,
                        "role": role,
                    },
                )
                user.full_name = full_name
                user.email = login
                user.role = role
                if created:
                    user.set_password(str(password).strip())
                user.save()

    def import_orders(self, base_path):
        path = self.first_file(base_path, "orders.csv", "order_import.csv", "Заказ_import.csv")
        if not path:
            self.stdout.write(self.style.WARNING("Файл заказов не найден."))
            return

        with open(path, encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file, delimiter=self.get_delimiter(file))
            for row in reader:
                print(row)
                order_id = self.integer(self.value(row, "id", "номер заказа"))
                if not order_id:
                    continue

                pp_raw = self.value(row, "pp", "pickup_point", "адрес пункта выдачи")
                pp_obj = self.get_pickup_point(pp_raw)
                client_name = self.value(
                    row,
                    "client_name",
                    "фио авторизированного клиента",
                    "фио клиента",
                )
                client = User.objects.filter(full_name=client_name).first()
                status_raw = self.value(row, "status", "статус заказа").lower()

                order, created = Order.objects.update_or_create(
                    id=order_id,
                    defaults={
                        "order_date": self.date_value(self.value(row, "order_date", "дата заказа")),
                        "delivery_date": self.date_value(
                            self.value(row, "delivery_date", "дата доставки")
                        ),
                        "client": client,
                        "client_name": client_name,
                        "pickup_code": self.integer(
                            self.value(row, "pickup_code", "код для получения")
                        ),
                        "status": STATUS_MAP.get(status_raw, Order.STATUS_NEW),
                        "pickup_point": pp_obj,
                    },
                )

                OrderItem.objects.filter(order=order).delete()
                items = self.value(row, "items", "артикул заказа").split(",")
                # Поле "Артикул заказа" хранит пары: артикул, количество; по заданию выводим 2 позиции.
                for index in range(0, min(len(items), 4), 2):
                    article = items[index].strip()
                    try:
                        count = self.integer(items[index + 1])
                        product = Product.objects.get(article=article)
                        OrderItem.objects.create(order=order, product=product, count=count or 1)
                    except Exception:
                        pass

                if created:
                    self.stdout.write(f"Создан заказ #{order.id}")

    def reset_sequences(self):
        sequence_sql = connection.ops.sequence_reset_sql(no_style(), [Order])
        with connection.cursor() as cursor:
            for sql in sequence_sql:
                cursor.execute(sql)

    def get_pickup_point(self, value):
        value = str(value or "").strip()
        if value.isdigit():
            # В заказах пункт выдачи может быть записан номером строки из файла, а не ID из БД.
            point = PickupPoint.objects.filter(id=int(value)).first()
            if point:
                return point

            index = int(value) - 1
            points = list(PickupPoint.objects.order_by("id"))
            if 0 <= index < len(points):
                return points[index]

        if value:
            point = PickupPoint.objects.filter(address__icontains=value).first()
            if point:
                return point
        return PickupPoint.objects.first() or PickupPoint.objects.create(address="Пункт выдачи")

    def first_file(self, base_path, *names):
        for name in names:
            path = os.path.join(base_path, name)
            if os.path.exists(path):
                return path
        return None

    def get_delimiter(self, file):
        first_line = file.readline()
        file.seek(0)
        return ";" if ";" in first_line else ","

    def value(self, row, *names):
        # Заголовки в выданных CSV отличаются языком и регистром, поэтому сравниваем нормализованно.
        normalized = {self.key(key): value for key, value in row.items() if key}
        for name in names:
            value = normalized.get(self.key(name))
            if value not in (None, ""):
                return str(value).strip()
        return ""

    def key(self, value):
        return str(value).strip().lower().replace("ё", "е").replace("_", " ")

    def decimal(self, value):
        return str(value or "0").replace(",", ".").replace("%", "").strip() or "0"

    def integer(self, value):
        try:
            return int(float(str(value or "0").replace(",", ".")))
        except ValueError:
            return 0

    def date_value(self, value):
        value = str(value or "").strip()
        for date_format in ("%d.%m.%Y", "%Y-%m-%d", "%d/%m/%Y"):
            try:
                return datetime.strptime(value, date_format).date()
            except ValueError:
                pass
        return datetime.now().date()
