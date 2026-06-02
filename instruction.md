# Полная пошаговая инструкция: Демоэкзамен 09.02.07 — ООО «Обувь»

> **Стек:** Python 3.13 · Django · PostgreSQL (Windows) · UV · VS Code  
> **Время на экзамене:** до 5 часов (4ч инвариант + 1ч вариатив)  
> **Максимум баллов:** 100 (75 инвариант + 25 вариатив)

---

## СОДЕРЖАНИЕ

1. [Подготовка до экзамена](#1-подготовка-до-экзамена)
2. [Настройка PostgreSQL на Windows](#2-настройка-postgresql-на-windows)
3. [Создание проекта с UV](#3-создание-проекта-с-uv)
4. [Модуль 1 — База данных и ER-диаграмма](#4-модуль-1--база-данных-и-er-диаграмма)
5. [Модуль 1 — Django модели и миграции](#5-модуль-1--django-модели-и-миграции)
6. [Модуль 1 — Скрипт импорта CSV (вариатив)](#6-модуль-1--скрипт-импорта-csv-вариатив)
7. [Модуль 2 — Авторизация и базовый интерфейс](#7-модуль-2--авторизация-и-базовый-интерфейс)
8. [Модуль 2 — Список товаров с подсветкой](#8-модуль-2--список-товаров-с-подсветкой)
9. [Модуль 3 — Поиск, фильтрация, сортировка](#9-модуль-3--поиск-фильтрация-сортировка)
10. [Модуль 3 — Форма добавления/редактирования товара + Pillow](#10-модуль-3--форма-добавленияредактирования-товара--pillow)
11. [Модуль 3 — Удаление товара](#11-модуль-3--удаление-товара)
12. [Модуль 4 — Заказы](#12-модуль-4--заказы)
13. [Вариативная часть — CSRF, неиспользуемые фото](#13-вариативная-часть--csrf-неиспользуемые-фото)
14. [Git и финальная сдача](#14-git-и-финальная-сдача)
15. [Чеклист перед сдачей](#15-чеклист-перед-сдачей)

---

## 1. Подготовка до экзамена

### Что должно быть установлено на экзаменационном ПК

- Python 3.13+ (проверить: `python --version`)
- PostgreSQL (уже установлен и запущен как служба Windows)
- VS Code
- Git
- UV (`pip install uv` или скачан заранее)
- draw.io (для ER-диаграммы, оффлайн версия)

### Ресурсы, которые дадут на экзамене (из Приложения 2)

- `picture.png` — картинка-заглушка для товаров без фото
- `Icon.png` / `Icon.ico` — иконка приложения
- Логотип компании
- CSV-файлы с пометкой `import` — данные для загрузки в БД

### Запомни цвета стиля (из руководства по стилю)

| Назначение | HEX |
|---|---|
| Основной фон | `#FFFFFF` |
| Дополнительный фон | `#7FFF00` |
| Акцент (целевое действие) | `#00FA9A` |
| Скидка > 15% (фон строки) | `#2E8B57` |
| Нет на складе (фон строки) | голубой (`lightblue`) |
| Перечёркнутая цена | красный шрифт |
| Итоговая цена со скидкой | чёрный шрифт |

Шрифт везде: **Times New Roman**

---

## 2. Настройка PostgreSQL на Windows

PostgreSQL уже установлен. Нужно только создать базу данных.

### Шаг 2.1 — Открыть PowerShell или cmd от имени администратора

```powershell
# Проверить, что PostgreSQL запущен
Get-Service -Name postgresql*
# Должно показать: Running
```

### Шаг 2.2 — Создать базу данных

```powershell
# Запустить psql от пользователя postgres
psql -U postgres
```

> [!WARNING]
> Если команда не работает стоит поискать psql как отдельную команду в проводнике или Пуске


Если psql не найден в PATH, найти его вручную:
```powershell
# Обычно находится здесь:
& "C:\Program Files\PostgreSQL\16\bin\psql.exe" -U postgres
```

Внутри psql выполнить:
```sql
CREATE DATABASE shoe_store OWNER postgres;
\q
```

### Шаг 2.3 — Запомнить данные подключения

```
HOST:     localhost
PORT:     5432
NAME:     shoe_store
USER:     postgres
PASSWORD: (пароль, который задавался при установке — обычно postgres)
```

> **Важно:** если не помнишь пароль, можно изменить его:  
> Открыть pgAdmin → щёлкнуть правой кнопкой на postgres → Change Password

---

## 3. Создание проекта с UV

### Шаг 3.1 — Создать папку проекта

```powershell
# В удобном месте (например, рабочий стол или C:\projects\)
mkdir shoe_store
cd shoe_store
```

### Шаг 3.2 — Инициализировать UV проект с venv

```powershell
# Инициализировать проект
uv init --no-readme

# UV автоматически создаёт .venv внутри папки
# Убедиться что venv создан:
uv venv
```

### Шаг 3.3 — Установить зависимости

```powershell
uv add django psycopg2-binary pillow
```

После этого в `pyproject.toml` появятся зависимости. Проверить:
```powershell
# Активировать venv для работы в терминале VS Code
.venv\Scripts\activate
```

> **VS Code:** открыть командную палитру (Ctrl+Shift+P) →  
> "Python: Select Interpreter" → выбрать `.venv\Scripts\python.exe`

### Шаг 3.4 — Создать Django проект

```powershell
# Убедиться что venv активирован (видно (.venv) в начале строки)
django-admin startproject config .
python manage.py startapp core
```

### Шаг 3.5 — Создать структуру папок

```powershell
# Папки для шаблонов
mkdir core\templates\core

# Папки для management команд (скрипт импорта CSV)
mkdir core\management
mkdir core\management\commands

# Создать __init__.py файлы
type nul > core\management\__init__.py
type nul > core\management\commands\__init__.py

# Папки для статики и медиа
mkdir static\css
mkdir static\images
mkdir media\products
```

### Шаг 3.6 — Настроить config/settings.py

Открыть `config/settings.py` и изменить/добавить следующее:

```python
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-your-secret-key-here'

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',  # наше приложение
]

# База данных PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'shoe_store',
        'USER': 'postgres',
        'PASSWORD': 'postgres',  # ваш пароль
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Язык и время
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

# Статические файлы (CSS, JS, иконки)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Медиафайлы (загружаемые фото товаров)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# После входа перенаправлять на список товаров
LOGIN_URL = '/'
LOGIN_REDIRECT_URL = '/products/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
```

### Шаг 3.7 — Скопировать ресурсы в static/images/

Из архива Приложения 2 скопировать:
- `picture.png` → `static/images/picture.png`
- `Icon.png` → `static/images/Icon.png`
- `Icon.ico` → `static/images/Icon.ico`
- логотип → `static/images/logo.png` (или как называется в ресурсах)

---

## 4. Модуль 1 — База данных и ER-диаграмма

### Схема БД (7 таблиц, 3НФ)

Прежде чем писать модели, нарисуй ER-диаграмму в draw.io.

**Таблицы:**

| Таблица | Поля |
|---|---|
| `role` | id, name (guest/client/manager/admin) |
| `user` | id, last_name, first_name, middle_name, login, password, role_id (FK) |
| `category` | id, name |
| `manufacturer` | id, name |
| `supplier` | id, name |
| `product` | id, name, category_id (FK), description, manufacturer_id (FK), supplier_id (FK), price, unit, quantity, discount, image_path |
| `pickup_point` | id, address |
| `order` | id, article, status, pickup_point_id (FK), order_date, delivery_date |
| `order_item` | id, order_id (FK), product_id (FK) |

**Связи:**
- user → role (многие к одному)
- product → category (многие к одному)
- product → manufacturer (многие к одному)
- product → supplier (многие к одному)
- order → pickup_point (многие к одному)
- order_item → order (многие к одному)
- order_item → product (многие к одному)

### Создание ER-диаграммы в draw.io

1. Открыть draw.io (десктопная версия или diagrams.net)
2. Создать новую диаграмму → выбрать Entity Relationship
3. Добавить таблицы с полями, обозначить PK и FK
4. Нарисовать связи между таблицами
5. Экспортировать: File → Export as → PDF
6. Сохранить как `er_diagram.pdf`

---

## 5. Модуль 1 — Django модели и миграции

### Шаг 5.1 — Написать models.py

Открыть `core/models.py` и заменить содержимое:

```python
from django.db import models


class Role(models.Model):
    """Роль пользователя в системе"""
    name = models.CharField(max_length=50, unique=True, verbose_name='Название роли')

    class Meta:
        db_table = 'role'
        verbose_name = 'Роль'
        verbose_name_plural = 'Роли'

    def __str__(self):
        return self.name


class User(models.Model):
    """Пользователь системы"""
    last_name = models.CharField(max_length=100, verbose_name='Фамилия')
    first_name = models.CharField(max_length=100, verbose_name='Имя')
    middle_name = models.CharField(max_length=100, blank=True, verbose_name='Отчество')
    login = models.CharField(max_length=100, unique=True, verbose_name='Логин')
    password = models.CharField(max_length=255, verbose_name='Пароль')
    role = models.ForeignKey(Role, on_delete=models.PROTECT, verbose_name='Роль')

    class Meta:
        db_table = 'user'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.last_name} {self.first_name}'

    def get_full_name(self):
        """Возвращает ФИО пользователя"""
        parts = [self.last_name, self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        return ' '.join(parts)


class Category(models.Model):
    """Категория товара"""
    name = models.CharField(max_length=100, unique=True, verbose_name='Название')

    class Meta:
        db_table = 'category'
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Manufacturer(models.Model):
    """Производитель товара"""
    name = models.CharField(max_length=200, unique=True, verbose_name='Название')

    class Meta:
        db_table = 'manufacturer'
        verbose_name = 'Производитель'
        verbose_name_plural = 'Производители'

    def __str__(self):
        return self.name


class Supplier(models.Model):
    """Поставщик товара"""
    name = models.CharField(max_length=200, unique=True, verbose_name='Название')

    class Meta:
        db_table = 'supplier'
        verbose_name = 'Поставщик'
        verbose_name_plural = 'Поставщики'

    def __str__(self):
        return self.name


class Product(models.Model):
    """Товар (обувь)"""
    name = models.CharField(max_length=200, verbose_name='Наименование')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, verbose_name='Категория')
    description = models.TextField(blank=True, verbose_name='Описание')
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.PROTECT, verbose_name='Производитель')
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, verbose_name='Поставщик')
    # Цена не может быть отрицательной
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    unit = models.CharField(max_length=50, default='пара', verbose_name='Единица измерения')
    # Количество не может быть отрицательным
    quantity = models.PositiveIntegerField(default=0, verbose_name='Количество на складе')
    # Скидка в процентах (0-100)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name='Скидка (%)')
    # Путь к изображению хранится в БД
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name='Фото')

    class Meta:
        db_table = 'product'
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self):
        return self.name

    def get_final_price(self):
        """Вычисляет итоговую цену с учётом скидки"""
        if self.discount > 0:
            return self.price * (1 - self.discount / 100)
        return self.price

    def has_discount(self):
        """Проверяет, есть ли скидка на товар"""
        return self.discount > 0

    def is_big_discount(self):
        """Проверяет, превышает ли скидка 15%"""
        return self.discount > 15

    def is_in_stock(self):
        """Проверяет, есть ли товар на складе"""
        return self.quantity > 0


class PickupPoint(models.Model):
    """Пункт выдачи заказа"""
    address = models.CharField(max_length=500, verbose_name='Адрес')

    class Meta:
        db_table = 'pickup_point'
        verbose_name = 'Пункт выдачи'
        verbose_name_plural = 'Пункты выдачи'

    def __str__(self):
        return self.address


class Order(models.Model):
    """Заказ"""
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('processing', 'В обработке'),
        ('ready', 'Готов к выдаче'),
        ('completed', 'Выполнен'),
        ('cancelled', 'Отменён'),
    ]

    article = models.CharField(max_length=100, unique=True, verbose_name='Артикул')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='new', verbose_name='Статус')
    pickup_point = models.ForeignKey(
        PickupPoint, on_delete=models.PROTECT, verbose_name='Пункт выдачи'
    )
    order_date = models.DateField(verbose_name='Дата заказа')
    delivery_date = models.DateField(null=True, blank=True, verbose_name='Дата выдачи')

    class Meta:
        db_table = 'order'
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f'Заказ {self.article}'


class OrderItem(models.Model):
    """Позиция в заказе (товар в заказе)"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='Заказ')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name='Товар')

    class Meta:
        db_table = 'order_item'
        verbose_name = 'Позиция заказа'
        verbose_name_plural = 'Позиции заказов'

    def __str__(self):
        return f'{self.order} — {self.product}'
```

### Шаг 5.2 — Выполнить миграции

```powershell
python manage.py makemigrations
python manage.py migrate
```

Если всё прошло без ошибок — таблицы созданы в PostgreSQL.

### Шаг 5.3 — Сгенерировать SQL-скрипт БД

```powershell
# Создать дамп схемы (только структура, без данных)
pg_dump -U postgres -s shoe_store > schema.sql

# Создать полный дамп (структура + данные, после импорта CSV)
pg_dump -U postgres shoe_store > full_dump.sql
```

Если pg_dump не в PATH:
```powershell
& "C:\Program Files\PostgreSQL\16\bin\pg_dump.exe" -U postgres -s shoe_store > schema.sql
```

---

## 6. Модуль 1 — Скрипт импорта CSV (вариатив)

Создать файл `core/management/commands/import_data.py`:

```python
import csv
import os
from django.core.management.base import BaseCommand
from core.models import Role, User, Category, Manufacturer, Supplier, Product, PickupPoint


class Command(BaseCommand):
    """Management-команда для импорта данных из CSV файлов"""
    help = 'Импорт данных из CSV файлов в базу данных'

    def handle(self, *args, **options):
        self.stdout.write('Начало импорта данных...')

        # Путь к папке с CSV файлами (положить рядом с manage.py)
        csv_dir = os.path.join(os.path.dirname(os.path.dirname(
            os.path.dirname(os.path.dirname(__file__))
        )), 'import_data')

        self.import_roles(csv_dir)
        self.import_categories(csv_dir)
        self.import_manufacturers(csv_dir)
        self.import_suppliers(csv_dir)
        self.import_users(csv_dir)
        self.import_products(csv_dir)
        self.import_pickup_points(csv_dir)

        self.stdout.write(self.style.SUCCESS('Импорт завершён успешно!'))

    def import_roles(self, csv_dir):
        """Импорт ролей пользователей"""
        file_path = os.path.join(csv_dir, 'roles.csv')
        if not os.path.exists(file_path):
            # Создаём роли по умолчанию если файл не найден
            default_roles = ['guest', 'client', 'manager', 'admin']
            for role_name in default_roles:
                Role.objects.get_or_create(name=role_name)
            self.stdout.write('Роли созданы по умолчанию')
            return

        with open(file_path, encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                Role.objects.get_or_create(name=row['name'])
        self.stdout.write('Роли импортированы')

    def import_categories(self, csv_dir):
        """Импорт категорий товаров"""
        file_path = os.path.join(csv_dir, 'categories.csv')
        if not os.path.exists(file_path):
            self.stdout.write(self.style.WARNING(f'Файл {file_path} не найден, пропуск'))
            return

        with open(file_path, encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                Category.objects.get_or_create(name=row['name'])
        self.stdout.write('Категории импортированы')

    def import_manufacturers(self, csv_dir):
        """Импорт производителей"""
        file_path = os.path.join(csv_dir, 'manufacturers.csv')
        if not os.path.exists(file_path):
            self.stdout.write(self.style.WARNING(f'Файл {file_path} не найден, пропуск'))
            return

        with open(file_path, encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                Manufacturer.objects.get_or_create(name=row['name'])
        self.stdout.write('Производители импортированы')

    def import_suppliers(self, csv_dir):
        """Импорт поставщиков"""
        file_path = os.path.join(csv_dir, 'suppliers.csv')
        if not os.path.exists(file_path):
            self.stdout.write(self.style.WARNING(f'Файл {file_path} не найден, пропуск'))
            return

        with open(file_path, encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                Supplier.objects.get_or_create(name=row['name'])
        self.stdout.write('Поставщики импортированы')

    def import_users(self, csv_dir):
        """Импорт пользователей"""
        file_path = os.path.join(csv_dir, 'users.csv')
        if not os.path.exists(file_path):
            self.stdout.write(self.style.WARNING(f'Файл {file_path} не найден, пропуск'))
            return

        with open(file_path, encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                role = Role.objects.get(name=row['role'])
                User.objects.get_or_create(
                    login=row['login'],
                    defaults={
                        'last_name': row['last_name'],
                        'first_name': row['first_name'],
                        'middle_name': row.get('middle_name', ''),
                        'password': row['password'],
                        'role': role,
                    }
                )
        self.stdout.write('Пользователи импортированы')

    def import_products(self, csv_dir):
        """Импорт товаров"""
        file_path = os.path.join(csv_dir, 'products.csv')
        if not os.path.exists(file_path):
            self.stdout.write(self.style.WARNING(f'Файл {file_path} не найден, пропуск'))
            return

        with open(file_path, encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                category = Category.objects.get(name=row['category'])
                manufacturer = Manufacturer.objects.get(name=row['manufacturer'])
                supplier = Supplier.objects.get(name=row['supplier'])
                Product.objects.get_or_create(
                    name=row['name'],
                    defaults={
                        'category': category,
                        'description': row.get('description', ''),
                        'manufacturer': manufacturer,
                        'supplier': supplier,
                        'price': row['price'],
                        'unit': row.get('unit', 'пара'),
                        'quantity': int(row.get('quantity', 0)),
                        'discount': row.get('discount', 0),
                    }
                )
        self.stdout.write('Товары импортированы')

    def import_pickup_points(self, csv_dir):
        """Импорт пунктов выдачи"""
        file_path = os.path.join(csv_dir, 'pickup_points.csv')
        if not os.path.exists(file_path):
            self.stdout.write(self.style.WARNING(f'Файл {file_path} не найден, пропуск'))
            return

        with open(file_path, encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                PickupPoint.objects.get_or_create(address=row['address'])
        self.stdout.write('Пункты выдачи импортированы')
```

Запустить импорт:
```powershell
# Создать папку import_data рядом с manage.py и положить туда CSV файлы
mkdir import_data
# Скопировать CSV файлы из ресурсов экзамена в папку import_data

python manage.py import_data
```

> **Важно:** структура CSV (разделитель, названия колонок) зависит от реальных файлов на экзамене.  
> Открой CSV в блокноте и подстрой `DictReader` под реальные заголовки.

---

## 7. Модуль 2 — Авторизация и базовый интерфейс

### Шаг 7.1 — Создать базовый шаблон base.html

Создать `core/templates/core/base.html`:

```html
{% load static %}
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}ООО Обувь{% endblock %}</title>
    <!-- Иконка приложения -->
    <link rel="icon" type="image/x-icon" href="{% static 'images/Icon.ico' %}">
    <link rel="stylesheet" href="{% static 'css/style.css' %}">
</head>
<body>
    <!-- Шапка с логотипом и ФИО пользователя -->
    <header class="header">
        <div class="header-left">
            <img src="{% static 'images/logo.png' %}" alt="Логотип ООО Обувь" class="logo">
            <span class="company-name">ООО «Обувь»</span>
        </div>
        <div class="header-right">
            {% if request.session.user_id %}
                <!-- ФИО пользователя в правом верхнем углу -->
                <span class="user-name">{{ request.session.user_full_name }}</span>
                <a href="{% url 'logout' %}" class="btn-logout">Выйти</a>
            {% endif %}
        </div>
    </header>

    <main class="main-content">
        <!-- Сообщения об ошибках и успехе -->
        {% if messages %}
            {% for message in messages %}
                <div class="message message-{{ message.tags }}">{{ message }}</div>
            {% endfor %}
        {% endif %}

        {% block content %}{% endblock %}
    </main>
</body>
</html>
```

### Шаг 7.2 — Создать шаблон login.html

Создать `core/templates/core/login.html`:

```html
{% load static %}
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Вход — ООО Обувь</title>
    <link rel="icon" type="image/x-icon" href="{% static 'images/Icon.ico' %}">
    <link rel="stylesheet" href="{% static 'css/style.css' %}">
</head>
<body>
    <div class="login-page">
        <!-- Логотип на главной форме -->
        <div class="login-logo">
            <img src="{% static 'images/logo.png' %}" alt="Логотип" class="logo-large">
        </div>

        <div class="login-container">
            <h1 class="login-title">Вход в систему</h1>

            <!-- Форма авторизации — CSRF токен обязателен -->
            <form method="post" action="{% url 'login' %}">
                {% csrf_token %}

                {% if error %}
                    <div class="error-message">{{ error }}</div>
                {% endif %}

                <div class="form-group">
                    <label for="login">Логин:</label>
                    <input type="text" id="login" name="login"
                           placeholder="Введите логин" required>
                </div>

                <div class="form-group">
                    <label for="password">Пароль:</label>
                    <input type="password" id="password" name="password"
                           placeholder="Введите пароль" required>
                </div>

                <div class="form-buttons">
                    <button type="submit" class="btn btn-accent">Войти</button>
                    <!-- Кнопка для входа как гость -->
                    <a href="{% url 'products_guest' %}" class="btn btn-secondary">
                        Войти как гость
                    </a>
                </div>
            </form>
        </div>
    </div>
</body>
</html>
```

### Шаг 7.3 — Создать views.py

Создать/заменить `core/views.py`:

```python
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseForbidden
from PIL import Image

from .models import Product, Category, Manufacturer, Supplier, Order, PickupPoint, OrderItem
from .forms import ProductForm, OrderForm


# ==================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ====================

def get_current_user_role(request):
    """Получает роль текущего пользователя из сессии"""
    return request.session.get('user_role', 'guest')


def require_role(view_func, allowed_roles):
    """Декоратор: проверяет роль пользователя"""
    def wrapper(request, *args, **kwargs):
        role = get_current_user_role(request)
        if role not in allowed_roles:
            messages.error(request, 'У вас нет доступа к этой странице.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


# ==================== АВТОРИЗАЦИЯ ====================

def login_view(request):
    """Страница входа в систему"""
    if request.method == 'POST':
        login = request.POST.get('login', '').strip()
        password = request.POST.get('password', '').strip()

        if not login or not password:
            return render(request, 'core/login.html', {
                'error': 'Введите логин и пароль.'
            })

        try:
            from .models import User
            user = User.objects.select_related('role').get(login=login, password=password)
            # Сохраняем данные пользователя в сессию
            request.session['user_id'] = user.id
            request.session['user_role'] = user.role.name
            request.session['user_full_name'] = user.get_full_name()
            return redirect('product_list')
        except Exception:
            return render(request, 'core/login.html', {
                'error': 'Неверный логин или пароль. Проверьте введённые данные.'
            })

    return render(request, 'core/login.html')


def logout_view(request):
    """Выход из системы — очищаем сессию"""
    request.session.flush()
    return redirect('login')


# ==================== СПИСОК ТОВАРОВ ====================

def product_list_view(request):
    """
    Список товаров.
    Доступен всем ролям, но поиск/фильтр/сортировка только менеджеру и администратору.
    """
    role = get_current_user_role(request)
    products = Product.objects.select_related(
        'category', 'manufacturer', 'supplier'
    ).all()

    # Поиск, фильтрация, сортировка только для менеджера и администратора
    search_query = ''
    supplier_filter = ''
    sort_by = ''

    if role in ('manager', 'admin'):
        # Поиск по всем текстовым полям одновременно
        search_query = request.GET.get('search', '').strip()
        if search_query:
            from django.db.models import Q
            products = products.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(category__name__icontains=search_query) |
                Q(manufacturer__name__icontains=search_query) |
                Q(supplier__name__icontains=search_query) |
                Q(unit__icontains=search_query)
            )

        # Фильтрация по поставщику
        supplier_filter = request.GET.get('supplier', '').strip()
        if supplier_filter:
            products = products.filter(supplier__name=supplier_filter)

        # Сортировка по количеству на складе
        sort_by = request.GET.get('sort', '')
        if sort_by == 'quantity_asc':
            products = products.order_by('quantity')
        elif sort_by == 'quantity_desc':
            products = products.order_by('-quantity')

    # Все поставщики для выпадающего списка фильтра
    suppliers = Supplier.objects.all()

    context = {
        'products': products,
        'role': role,
        'suppliers': suppliers,
        'search_query': search_query,
        'supplier_filter': supplier_filter,
        'sort_by': sort_by,
        'user_full_name': request.session.get('user_full_name', ''),
    }
    return render(request, 'core/product_list.html', context)
```

### Шаг 7.4 — Настроить URLs

Открыть `config/urls.py`:

```python
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from core import views

urlpatterns = [
    # Авторизация
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Товары
    path('products/', views.product_list_view, name='product_list'),
    path('products/guest/', views.product_list_view, name='products_guest'),
    path('products/add/', views.product_create_view, name='product_create'),
    path('products/<int:pk>/edit/', views.product_update_view, name='product_edit'),
    path('products/<int:pk>/delete/', views.product_delete_view, name='product_delete'),

    # Заказы
    path('orders/', views.order_list_view, name='order_list'),
    path('orders/add/', views.order_create_view, name='order_create'),
    path('orders/<int:pk>/edit/', views.order_update_view, name='order_edit'),
    path('orders/<int:pk>/delete/', views.order_delete_view, name='order_delete'),
]

# Раздача медиафайлов в режиме разработки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

---

## 8. Модуль 2 — Список товаров с подсветкой

### Шаг 8.1 — Создать шаблон product_list.html

Создать `core/templates/core/product_list.html`:

```html
{% load static %}
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Список товаров — ООО Обувь</title>
    <link rel="icon" type="image/x-icon" href="{% static 'images/Icon.ico' %}">
    <link rel="stylesheet" href="{% static 'css/style.css' %}">
</head>
<body>
    <header class="header">
        <div class="header-left">
            <img src="{% static 'images/logo.png' %}" alt="Логотип" class="logo">
            <span class="company-name">ООО «Обувь»</span>
        </div>
        <div class="header-right">
            {% if user_full_name %}
                <span class="user-name">{{ user_full_name }}</span>
            {% endif %}
            {% if role != 'guest' %}
                <a href="{% url 'logout' %}" class="btn btn-secondary">Выйти</a>
            {% else %}
                <a href="{% url 'login' %}" class="btn btn-accent">Войти</a>
            {% endif %}
        </div>
    </header>

    <main class="main-content">
        <div class="page-header">
            <h1>Список товаров</h1>
            <div class="header-actions">
                <!-- Кнопка "Заказы" для менеджера и администратора -->
                {% if role in 'manager admin' or role == 'manager' or role == 'admin' %}
                    <a href="{% url 'order_list' %}" class="btn btn-secondary">Заказы</a>
                {% endif %}
                <!-- Кнопка "Добавить товар" только для администратора -->
                {% if role == 'admin' %}
                    <a href="{% url 'product_create' %}" class="btn btn-accent">+ Добавить товар</a>
                {% endif %}
            </div>
        </div>

        <!-- Панель поиска/фильтрации/сортировки (только менеджер и администратор) -->
        {% if role == 'manager' or role == 'admin' %}
        <div class="filters-panel">
            <!-- Поиск в реальном времени через JavaScript -->
            <input type="text" id="search-input" placeholder="Поиск по всем полям..."
                   value="{{ search_query }}" class="search-input">

            <!-- Фильтр по поставщику -->
            <select id="supplier-filter" class="filter-select">
                <option value="">Все поставщики</option>
                {% for supplier in suppliers %}
                    <option value="{{ supplier.name }}"
                        {% if supplier.name == supplier_filter %}selected{% endif %}>
                        {{ supplier.name }}
                    </option>
                {% endfor %}
            </select>

            <!-- Сортировка по количеству -->
            <select id="sort-select" class="filter-select">
                <option value="">Без сортировки</option>
                <option value="quantity_asc" {% if sort_by == 'quantity_asc' %}selected{% endif %}>
                    Количество ↑
                </option>
                <option value="quantity_desc" {% if sort_by == 'quantity_desc' %}selected{% endif %}>
                    Количество ↓
                </option>
            </select>
        </div>
        {% endif %}

        <!-- Таблица товаров -->
        <div class="products-list">
            {% for product in products %}
                <!--
                    Логика подсветки строк:
                    - скидка > 15%: зелёный фон #2E8B57
                    - нет на складе: голубой фон
                    - иначе: белый фон
                -->
                <div class="product-card
                    {% if product.is_big_discount %}product-big-discount
                    {% elif not product.is_in_stock %}product-out-of-stock
                    {% endif %}"
                    {% if role == 'admin' %}
                        onclick="window.location='{% url 'product_edit' product.pk %}'"
                        style="cursor: pointer;"
                    {% endif %}>

                    <!-- Фото товара -->
                    <div class="product-image">
                        {% if product.image %}
                            <img src="{{ product.image.url }}" alt="{{ product.name }}">
                        {% else %}
                            <!-- Заглушка при отсутствии изображения -->
                            <img src="{% static 'images/picture.png' %}" alt="Нет фото">
                        {% endif %}
                    </div>

                    <!-- Информация о товаре -->
                    <div class="product-info">
                        <div class="product-title">
                            <strong>{{ product.category.name }} | {{ product.name }}</strong>
                        </div>
                        <div>Описание: {{ product.description|default:"—" }}</div>
                        <div>Производитель: {{ product.manufacturer.name }}</div>
                        <div>Поставщик: {{ product.supplier.name }}</div>

                        <!-- Цена: перечёркнутая если есть скидка -->
                        <div class="product-price">
                            {% if product.has_discount %}
                                <span class="price-original">{{ product.price }} ₽</span>
                                <span class="price-final">{{ product.get_final_price|floatformat:2 }} ₽</span>
                            {% else %}
                                <span>{{ product.price }} ₽</span>
                            {% endif %}
                        </div>

                        <div>Единица измерения: {{ product.unit }}</div>
                        <div>Количество на складе: {{ product.quantity }}</div>
                    </div>

                    <!-- Скидка -->
                    <div class="product-discount">
                        {% if product.has_discount %}
                            {{ product.discount }}%
                        {% else %}
                            —
                        {% endif %}
                    </div>

                    <!-- Кнопка удаления (только администратор) -->
                    {% if role == 'admin' %}
                        <div class="product-actions" onclick="event.stopPropagation()">
                            <form method="post" action="{% url 'product_delete' product.pk %}"
                                  onsubmit="return confirm('Удалить товар «{{ product.name }}»? Это действие необратимо.')">
                                {% csrf_token %}
                                <button type="submit" class="btn btn-danger">Удалить</button>
                            </form>
                        </div>
                    {% endif %}
                </div>
            {% empty %}
                <p class="no-results">Товары не найдены.</p>
            {% endfor %}
        </div>
    </main>

    <!-- JavaScript для поиска/фильтрации/сортировки в реальном времени -->
    {% if role == 'manager' or role == 'admin' %}
    <script>
        // Функция обновления URL с параметрами без перезагрузки страницы
        function updateFilters() {
            const search = document.getElementById('search-input').value;
            const supplier = document.getElementById('supplier-filter').value;
            const sort = document.getElementById('sort-select').value;

            // Перезагружаем страницу с новыми параметрами
            const params = new URLSearchParams();
            if (search) params.set('search', search);
            if (supplier) params.set('supplier', supplier);
            if (sort) params.set('sort', sort);

            window.location.href = '/products/?' + params.toString();
        }

        // Поиск в реальном времени (с небольшой задержкой debounce)
        let searchTimeout;
        document.getElementById('search-input').addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(updateFilters, 300);
        });

        // Фильтр и сортировка срабатывают сразу при изменении
        document.getElementById('supplier-filter').addEventListener('change', updateFilters);
        document.getElementById('sort-select').addEventListener('change', updateFilters);
    </script>
    {% endif %}
</body>
</html>
```

### Шаг 8.2 — Создать CSS стили

Создать `static/css/style.css`:

```css
/* Основные настройки — шрифт Times New Roman, белый фон */
* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    font-family: 'Times New Roman', Times, serif;
    background-color: #FFFFFF;   /* Основной фон */
    color: #333;
}

/* ========== ШАПКА ========== */
.header {
    background-color: #7FFF00;   /* Дополнительный фон */
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 20px;
    border-bottom: 2px solid #ccc;
}

.header-left {
    display: flex;
    align-items: center;
    gap: 10px;
}

.logo {
    height: 50px;
    width: auto;       /* Сохраняем пропорции логотипа */
    object-fit: contain;
}

.logo-large {
    height: 80px;
    width: auto;
    object-fit: contain;
}

.company-name {
    font-size: 1.3em;
    font-weight: bold;
}

.header-right {
    display: flex;
    align-items: center;
    gap: 15px;
}

.user-name {
    font-weight: bold;
    font-size: 1em;
}

/* ========== КНОПКИ ========== */
.btn {
    display: inline-block;
    padding: 8px 16px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-family: 'Times New Roman', Times, serif;
    font-size: 1em;
    text-decoration: none;
    text-align: center;
}

.btn-accent {
    background-color: #00FA9A;   /* Акцентирование внимания */
    color: #000;
}

.btn-secondary {
    background-color: #7FFF00;   /* Дополнительный фон */
    color: #000;
}

.btn-danger {
    background-color: #dc3545;
    color: #fff;
}

.btn-logout {
    background-color: #f8f9fa;
    color: #333;
    padding: 6px 12px;
    border-radius: 4px;
    text-decoration: none;
    border: 1px solid #ccc;
}

/* ========== ОСНОВНОЕ СОДЕРЖИМОЕ ========== */
.main-content {
    padding: 20px;
    max-width: 1200px;
    margin: 0 auto;
}

.page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

.header-actions {
    display: flex;
    gap: 10px;
}

/* ========== СТРАНИЦА ВХОДА ========== */
.login-page {
    min-height: 100vh;
    background-color: #7FFF00;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 20px;
}

.login-logo {
    margin-bottom: 20px;
}

.login-container {
    background-color: #FFFFFF;
    padding: 30px;
    border-radius: 8px;
    width: 100%;
    max-width: 400px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.login-title {
    text-align: center;
    margin-bottom: 20px;
    font-size: 1.5em;
}

.form-group {
    margin-bottom: 15px;
}

.form-group label {
    display: block;
    margin-bottom: 5px;
    font-weight: bold;
}

.form-group input,
.form-group select,
.form-group textarea {
    width: 100%;
    padding: 8px;
    border: 1px solid #ccc;
    border-radius: 4px;
    font-family: 'Times New Roman', Times, serif;
    font-size: 1em;
}

.form-buttons {
    display: flex;
    gap: 10px;
    justify-content: center;
    margin-top: 20px;
}

.error-message {
    background-color: #f8d7da;
    color: #721c24;
    padding: 10px;
    border-radius: 4px;
    margin-bottom: 15px;
    border: 1px solid #f5c6cb;
}

/* ========== ПАНЕЛЬ ФИЛЬТРОВ ========== */
.filters-panel {
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
    align-items: center;
    flex-wrap: wrap;
}

.search-input {
    flex: 1;
    min-width: 200px;
    padding: 8px;
    border: 1px solid #ccc;
    border-radius: 4px;
    font-family: 'Times New Roman', Times, serif;
    font-size: 1em;
}

.filter-select {
    padding: 8px;
    border: 1px solid #ccc;
    border-radius: 4px;
    font-family: 'Times New Roman', Times, serif;
    font-size: 1em;
}

/* ========== КАРТОЧКА ТОВАРА ========== */
.products-list {
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.product-card {
    display: flex;
    align-items: stretch;
    border: 1px solid #ccc;
    border-radius: 4px;
    background-color: #FFFFFF;
    overflow: hidden;
}

/* Скидка > 15% — зелёный фон */
.product-big-discount {
    background-color: #2E8B57;
    color: #fff;
}

/* Нет на складе — голубой фон */
.product-out-of-stock {
    background-color: lightblue;
}

.product-image {
    width: 120px;
    min-width: 120px;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 10px;
    background-color: rgba(255,255,255,0.3);
}

.product-image img {
    width: 100px;
    height: 80px;
    object-fit: contain;
}

.product-info {
    flex: 1;
    padding: 10px;
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.product-title {
    font-size: 1.1em;
    margin-bottom: 5px;
}

/* Цена со скидкой */
.price-original {
    text-decoration: line-through;   /* Перечёркнутая цена */
    color: red;                        /* Красный шрифт */
    margin-right: 8px;
}

.price-final {
    color: black;                      /* Итоговая цена чёрным */
    font-weight: bold;
}

.product-discount {
    width: 80px;
    min-width: 80px;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 10px;
    font-size: 1.1em;
    font-weight: bold;
    border-left: 1px solid #ccc;
}

.product-actions {
    display: flex;
    align-items: center;
    padding: 10px;
    border-left: 1px solid #ccc;
}

.no-results {
    text-align: center;
    color: #666;
    padding: 40px;
    font-size: 1.2em;
}

/* ========== ФОРМА ТОВАРА ========== */
.form-container {
    max-width: 700px;
    margin: 0 auto;
}

.form-container h1 {
    margin-bottom: 20px;
}

.form-image-preview {
    width: 300px;
    height: 200px;
    object-fit: contain;
    border: 1px solid #ccc;
    margin-bottom: 10px;
}

.field-readonly {
    background-color: #f5f5f5;
    cursor: not-allowed;
}

/* ========== СПИСОК ЗАКАЗОВ ========== */
.order-card {
    display: flex;
    align-items: stretch;
    border: 1px solid #ccc;
    border-radius: 4px;
    background-color: #FFFFFF;
    margin-bottom: 10px;
    overflow: hidden;
}

.order-info {
    flex: 1;
    padding: 10px;
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.order-delivery {
    width: 150px;
    min-width: 150px;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 10px;
    border-left: 1px solid #ccc;
    font-weight: bold;
}

/* ========== СООБЩЕНИЯ ========== */
.message {
    padding: 10px 15px;
    border-radius: 4px;
    margin-bottom: 15px;
}

.message-success {
    background-color: #d4edda;
    color: #155724;
    border: 1px solid #c3e6cb;
}

.message-error {
    background-color: #f8d7da;
    color: #721c24;
    border: 1px solid #f5c6cb;
}

.message-warning {
    background-color: #fff3cd;
    color: #856404;
    border: 1px solid #ffeeba;
}
```

---

## 9. Модуль 3 — Поиск, фильтрация, сортировка

Поиск, фильтрация и сортировка уже реализованы в `product_list_view` (шаг 7.3) и в шаблоне (шаг 8.1) через JavaScript. Убедиться что:

- Поиск работает по всем текстовым полям одновременно (`Q` объекты в `filter`)
- Фильтр по поставщику: первый элемент "Все поставщики" (value=""), при выборе которого фильтр сбрасывается
- Сортировка по количеству: вверх/вниз
- Всё происходит в реальном времени через `debounce` 300ms в JavaScript
- Параметры сортировки сохраняются при изменении поиска и фильтра (через `URLSearchParams`)

---

## 10. Модуль 3 — Форма добавления/редактирования товара + Pillow

### Шаг 10.1 — Создать forms.py

Создать `core/forms.py`:

```python
from django import forms
from .models import Product, Order, PickupPoint


class ProductForm(forms.ModelForm):
    """Форма добавления/редактирования товара"""

    class Meta:
        model = Product
        fields = [
            'name', 'category', 'description', 'manufacturer',
            'supplier', 'price', 'unit', 'quantity', 'discount', 'image'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите наименование товара'
            }),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Введите описание товара'
            }),
            'manufacturer': forms.Select(attrs={'class': 'form-control'}),
            'supplier': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите поставщика'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'unit': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например: пара, штука'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': '0'
            }),
            'discount': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '100',
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }

    def clean_price(self):
        """Цена не может быть отрицательной"""
        price = self.cleaned_data.get('price')
        if price is not None and price < 0:
            raise forms.ValidationError('Цена не может быть отрицательной.')
        return price

    def clean_quantity(self):
        """Количество не может быть отрицательным"""
        quantity = self.cleaned_data.get('quantity')
        if quantity is not None and quantity < 0:
            raise forms.ValidationError('Количество не может быть отрицательным.')
        return quantity

    def clean_discount(self):
        """Скидка должна быть от 0 до 100"""
        discount = self.cleaned_data.get('discount')
        if discount is not None and (discount < 0 or discount > 100):
            raise forms.ValidationError('Скидка должна быть от 0 до 100.')
        return discount


class OrderForm(forms.ModelForm):
    """Форма добавления/редактирования заказа"""

    class Meta:
        model = Order
        fields = ['article', 'status', 'pickup_point', 'order_date', 'delivery_date']
        widgets = {
            'article': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'pickup_point': forms.Select(attrs={'class': 'form-control'}),
            'order_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'delivery_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }
```

### Шаг 10.2 — Добавить views для товаров в views.py

Добавить в `core/views.py`:

```python
def product_create_view(request):
    """Создание нового товара — только для администратора"""
    role = get_current_user_role(request)
    if role != 'admin':
        messages.error(request, 'Добавлять товары может только администратор.')
        return redirect('product_list')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            # Обработка изображения через Pillow (ресайз 300x200)
            if 'image' in request.FILES:
                product = resize_product_image(product, request.FILES['image'])
            product.save()
            messages.success(request, f'Товар «{product.name}» успешно добавлен.')
            return redirect('product_list')
    else:
        form = ProductForm()

    return render(request, 'core/product_form.html', {
        'form': form,
        'title': 'Добавить товар',
        'is_create': True,
        'role': role,
        'user_full_name': request.session.get('user_full_name', ''),
    })


def product_update_view(request, pk):
    """Редактирование товара — только для администратора"""
    role = get_current_user_role(request)
    if role != 'admin':
        messages.error(request, 'Редактировать товары может только администратор.')
        return redirect('product_list')

    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            updated_product = form.save(commit=False)
            # Если загружено новое изображение — удалить старое и сохранить новое
            if 'image' in request.FILES:
                # Удаляем старое фото с диска
                if product.image and os.path.isfile(product.image.path):
                    os.remove(product.image.path)
                updated_product = resize_product_image(updated_product, request.FILES['image'])
            updated_product.save()
            messages.success(request, f'Товар «{product.name}» успешно обновлён.')
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)

    return render(request, 'core/product_form.html', {
        'form': form,
        'product': product,
        'title': f'Редактировать товар: {product.name}',
        'is_create': False,
        'role': role,
        'user_full_name': request.session.get('user_full_name', ''),
    })


def resize_product_image(product, image_file):
    """
    Обрабатывает изображение через Pillow:
    изменяет размер до 300x200 пикселей и сохраняет.
    """
    from PIL import Image as PilImage
    from io import BytesIO
    from django.core.files.uploadedfile import InMemoryUploadedFile
    import sys

    # Открываем изображение через Pillow
    img = PilImage.open(image_file)

    # Изменяем размер до 300x200 (с сохранением пропорций через thumbnail)
    img = img.resize((300, 200), PilImage.LANCZOS)

    # Сохраняем обратно в память
    output = BytesIO()
    img_format = img.format if img.format else 'JPEG'
    img.save(output, format=img_format, quality=85)
    output.seek(0)

    # Создаём новый файл для Django
    product.image = InMemoryUploadedFile(
        output,
        'ImageField',
        image_file.name,
        f'image/{img_format.lower()}',
        sys.getsizeof(output),
        None
    )
    return product
```

### Шаг 10.3 — Создать шаблон product_form.html

Создать `core/templates/core/product_form.html`:

```html
{% load static %}
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>{{ title }} — ООО Обувь</title>
    <link rel="icon" type="image/x-icon" href="{% static 'images/Icon.ico' %}">
    <link rel="stylesheet" href="{% static 'css/style.css' %}">
</head>
<body>
    <header class="header">
        <div class="header-left">
            <img src="{% static 'images/logo.png' %}" alt="Логотип" class="logo">
            <span class="company-name">ООО «Обувь»</span>
        </div>
        <div class="header-right">
            <span class="user-name">{{ user_full_name }}</span>
            <a href="{% url 'logout' %}" class="btn btn-secondary">Выйти</a>
        </div>
    </header>

    <main class="main-content">
        <div class="form-container">
            <!-- Кнопка Назад -->
            <a href="{% url 'product_list' %}" class="btn btn-secondary" style="margin-bottom:15px;">
                ← Назад к списку
            </a>

            <h1>{{ title }}</h1>

            <form method="post" enctype="multipart/form-data">
                {% csrf_token %}

                <!-- ID товара: при добавлении не показываем, при редактировании — только чтение -->
                {% if not is_create %}
                    <div class="form-group">
                        <label>ID товара:</label>
                        <input type="text" value="{{ product.pk }}"
                               class="form-control field-readonly" readonly>
                    </div>
                {% endif %}

                <!-- Предпросмотр текущего фото -->
                <div class="form-group">
                    <label>Фото товара:</label>
                    {% if product.image %}
                        <img src="{{ product.image.url }}" alt="Текущее фото"
                             class="form-image-preview" id="image-preview">
                    {% else %}
                        <img src="{% static 'images/picture.png' %}" alt="Нет фото"
                             class="form-image-preview" id="image-preview">
                    {% endif %}
                    {{ form.image }}
                </div>

                <!-- Остальные поля формы -->
                <div class="form-group">
                    <label>Наименование товара: *</label>
                    {{ form.name }}
                    {% if form.name.errors %}
                        <div class="error-message">{{ form.name.errors }}</div>
                    {% endif %}
                </div>

                <div class="form-group">
                    <label>Категория товара: *</label>
                    {{ form.category }}
                </div>

                <div class="form-group">
                    <label>Описание товара:</label>
                    {{ form.description }}
                </div>

                <div class="form-group">
                    <label>Производитель: *</label>
                    {{ form.manufacturer }}
                </div>

                <div class="form-group">
                    <label>Поставщик: *</label>
                    {{ form.supplier }}
                </div>

                <div class="form-group">
                    <label>Цена (₽): * (не может быть отрицательной)</label>
                    {{ form.price }}
                    {% if form.price.errors %}
                        <div class="error-message">{{ form.price.errors }}</div>
                    {% endif %}
                </div>

                <div class="form-group">
                    <label>Единица измерения: *</label>
                    {{ form.unit }}
                </div>

                <div class="form-group">
                    <label>Количество на складе: * (не может быть отрицательным)</label>
                    {{ form.quantity }}
                    {% if form.quantity.errors %}
                        <div class="error-message">{{ form.quantity.errors }}</div>
                    {% endif %}
                </div>

                <div class="form-group">
                    <label>Скидка (%): (0–100)</label>
                    {{ form.discount }}
                    {% if form.discount.errors %}
                        <div class="error-message">{{ form.discount.errors }}</div>
                    {% endif %}
                </div>

                <div class="form-buttons">
                    <button type="submit" class="btn btn-accent">
                        {% if is_create %}Добавить товар{% else %}Сохранить изменения{% endif %}
                    </button>
                    <a href="{% url 'product_list' %}" class="btn btn-secondary">Отмена</a>
                </div>
            </form>
        </div>
    </main>

    <script>
        // Предпросмотр изображения при выборе файла
        document.querySelector('input[type=file]').addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    document.getElementById('image-preview').src = e.target.result;
                };
                reader.readAsDataURL(file);
            }
        });
    </script>
</body>
</html>
```

---

## 11. Модуль 3 — Удаление товара

Добавить в `core/views.py`:

```python
def product_delete_view(request, pk):
    """Удаление товара — только для администратора"""
    role = get_current_user_role(request)
    if role != 'admin':
        messages.error(request, 'Удалять товары может только администратор.')
        return redirect('product_list')

    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        # Проверяем: нельзя удалить товар, который есть в заказах
        if OrderItem.objects.filter(product=product).exists():
            messages.error(
                request,
                f'Нельзя удалить товар «{product.name}»: он присутствует в заказах. '
                f'Сначала удалите или измените связанные заказы.'
            )
            return redirect('product_list')

        # Удаляем файл изображения с диска
        if product.image and os.path.isfile(product.image.path):
            os.remove(product.image.path)

        product_name = product.name
        product.delete()
        messages.success(request, f'Товар «{product_name}» успешно удалён.')
        return redirect('product_list')

    # GET — показываем страницу подтверждения (или используем confirm в JS)
    return redirect('product_list')
```

---

## 12. Модуль 4 — Заказы

### Шаг 12.1 — Добавить views для заказов в views.py

Добавить в `core/views.py`:

```python
def order_list_view(request):
    """Список заказов — для менеджера и администратора"""
    role = get_current_user_role(request)
    if role not in ('manager', 'admin'):
        messages.error(request, 'Просматривать заказы могут только менеджер и администратор.')
        return redirect('login')

    orders = Order.objects.select_related('pickup_point').all()

    return render(request, 'core/order_list.html', {
        'orders': orders,
        'role': role,
        'user_full_name': request.session.get('user_full_name', ''),
    })


def order_create_view(request):
    """Создание заказа — только для администратора"""
    role = get_current_user_role(request)
    if role != 'admin':
        messages.error(request, 'Добавлять заказы может только администратор.')
        return redirect('order_list')

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save()
            messages.success(request, f'Заказ «{order.article}» успешно создан.')
            return redirect('order_list')
    else:
        form = OrderForm()

    return render(request, 'core/order_form.html', {
        'form': form,
        'title': 'Добавить заказ',
        'is_create': True,
        'role': role,
        'user_full_name': request.session.get('user_full_name', ''),
    })


def order_update_view(request, pk):
    """Редактирование заказа — только для администратора"""
    role = get_current_user_role(request)
    if role != 'admin':
        messages.error(request, 'Редактировать заказы может только администратор.')
        return redirect('order_list')

    order = get_object_or_404(Order, pk=pk)

    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, f'Заказ «{order.article}» успешно обновлён.')
            return redirect('order_list')
    else:
        form = OrderForm(instance=order)

    return render(request, 'core/order_form.html', {
        'form': form,
        'order': order,
        'title': f'Редактировать заказ: {order.article}',
        'is_create': False,
        'role': role,
        'user_full_name': request.session.get('user_full_name', ''),
    })


def order_delete_view(request, pk):
    """Удаление заказа — только для администратора"""
    role = get_current_user_role(request)
    if role != 'admin':
        messages.error(request, 'Удалять заказы может только администратор.')
        return redirect('order_list')

    order = get_object_or_404(Order, pk=pk)

    if request.method == 'POST':
        article = order.article
        order.delete()
        messages.success(request, f'Заказ «{article}» успешно удалён.')
        return redirect('order_list')

    return redirect('order_list')
```

### Шаг 12.2 — Создать шаблоны заказов

Создать `core/templates/core/order_list.html`:

```html
{% load static %}
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Заказы — ООО Обувь</title>
    <link rel="icon" type="image/x-icon" href="{% static 'images/Icon.ico' %}">
    <link rel="stylesheet" href="{% static 'css/style.css' %}">
</head>
<body>
    <header class="header">
        <div class="header-left">
            <img src="{% static 'images/logo.png' %}" alt="Логотип" class="logo">
            <span class="company-name">ООО «Обувь»</span>
        </div>
        <div class="header-right">
            <span class="user-name">{{ user_full_name }}</span>
            <a href="{% url 'logout' %}" class="btn btn-secondary">Выйти</a>
        </div>
    </header>

    <main class="main-content">
        <div class="page-header">
            <h1>Заказы</h1>
            <div class="header-actions">
                <a href="{% url 'product_list' %}" class="btn btn-secondary">← Товары</a>
                {% if role == 'admin' %}
                    <a href="{% url 'order_create' %}" class="btn btn-accent">+ Добавить заказ</a>
                {% endif %}
            </div>
        </div>

        {% if messages %}
            {% for message in messages %}
                <div class="message message-{{ message.tags }}">{{ message }}</div>
            {% endfor %}
        {% endif %}

        <div class="orders-list">
            {% for order in orders %}
                <!-- Клик по заказу открывает редактирование (только у администратора) -->
                <div class="order-card"
                    {% if role == 'admin' %}
                        onclick="window.location='{% url 'order_edit' order.pk %}'"
                        style="cursor: pointer;"
                    {% endif %}>

                    <div class="order-info">
                        <div><strong>Артикул заказа: {{ order.article }}</strong></div>
                        <div>Статус заказа: {{ order.get_status_display }}</div>
                        <div>Адрес пункта выдачи: {{ order.pickup_point.address }}</div>
                        <div>Дата заказа: {{ order.order_date }}</div>
                    </div>

                    <div class="order-delivery">
                        Дата доставки:<br>
                        {{ order.delivery_date|default:"—" }}
                    </div>

                    {% if role == 'admin' %}
                        <div class="product-actions" onclick="event.stopPropagation()">
                            <form method="post" action="{% url 'order_delete' order.pk %}"
                                  onsubmit="return confirm('Удалить заказ «{{ order.article }}»?')">
                                {% csrf_token %}
                                <button type="submit" class="btn btn-danger">Удалить</button>
                            </form>
                        </div>
                    {% endif %}
                </div>
            {% empty %}
                <p class="no-results">Заказы не найдены.</p>
            {% endfor %}
        </div>
    </main>
</body>
</html>
```

Создать `core/templates/core/order_form.html`:

```html
{% load static %}
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>{{ title }} — ООО Обувь</title>
    <link rel="icon" type="image/x-icon" href="{% static 'images/Icon.ico' %}">
    <link rel="stylesheet" href="{% static 'css/style.css' %}">
</head>
<body>
    <header class="header">
        <div class="header-left">
            <img src="{% static 'images/logo.png' %}" alt="Логотип" class="logo">
            <span class="company-name">ООО «Обувь»</span>
        </div>
        <div class="header-right">
            <span class="user-name">{{ user_full_name }}</span>
            <a href="{% url 'logout' %}" class="btn btn-secondary">Выйти</a>
        </div>
    </header>

    <main class="main-content">
        <div class="form-container">
            <a href="{% url 'order_list' %}" class="btn btn-secondary" style="margin-bottom:15px;">
                ← Назад к заказам
            </a>

            <h1>{{ title }}</h1>

            <form method="post">
                {% csrf_token %}

                {% if not is_create %}
                    <div class="form-group">
                        <label>ID заказа:</label>
                        <input type="text" value="{{ order.pk }}"
                               class="form-control field-readonly" readonly>
                    </div>
                {% endif %}

                <div class="form-group">
                    <label>Артикул: *</label>
                    {{ form.article }}
                    {% if form.article.errors %}
                        <div class="error-message">{{ form.article.errors }}</div>
                    {% endif %}
                </div>

                <div class="form-group">
                    <label>Статус заказа: *</label>
                    {{ form.status }}
                </div>

                <div class="form-group">
                    <label>Адрес пункта выдачи: *</label>
                    {{ form.pickup_point }}
                </div>

                <div class="form-group">
                    <label>Дата заказа: *</label>
                    {{ form.order_date }}
                </div>

                <div class="form-group">
                    <label>Дата выдачи:</label>
                    {{ form.delivery_date }}
                </div>

                <div class="form-buttons">
                    <button type="submit" class="btn btn-accent">
                        {% if is_create %}Добавить заказ{% else %}Сохранить изменения{% endif %}
                    </button>
                    <a href="{% url 'order_list' %}" class="btn btn-secondary">Отмена</a>
                </div>
            </form>
        </div>
    </main>
</body>
</html>
```

---

## 13. Вариативная часть — CSRF, неиспользуемые фото

### CSRF-защита (5 баллов)

CSRF уже встроена в Django. Убедиться что:
- `django.middleware.csrf.CsrfViewMiddleware` есть в `MIDDLEWARE` в settings.py (там по умолчанию)
- В **каждой** POST-форме стоит `{% csrf_token %}`:
  - `login.html` — форма входа ✓
  - `product_list.html` — форма удаления ✓
  - `product_form.html` — форма товара ✓
  - `order_list.html` — форма удаления заказа ✓
  - `order_form.html` — форма заказа ✓

### Удаление неиспользуемых фото (5 баллов)

Создать management-команду `core/management/commands/cleanup_images.py`:

```python
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from core.models import Product


class Command(BaseCommand):
    """Удаление фотографий товаров, которые больше не используются в БД"""
    help = 'Удаление неиспользуемых изображений товаров из папки media/products/'

    def handle(self, *args, **options):
        # Получаем все пути к изображениям из базы данных
        db_images = set()
        for product in Product.objects.exclude(image='').exclude(image__isnull=True):
            if product.image:
                db_images.add(os.path.basename(product.image.name))

        # Получаем все файлы в папке media/products/
        products_dir = os.path.join(settings.MEDIA_ROOT, 'products')
        if not os.path.exists(products_dir):
            self.stdout.write('Папка media/products/ не найдена.')
            return

        deleted_count = 0
        for filename in os.listdir(products_dir):
            if filename not in db_images:
                # Файл не используется ни одним товаром — удаляем
                file_path = os.path.join(products_dir, filename)
                os.remove(file_path)
                deleted_count += 1
                self.stdout.write(f'Удалён: {filename}')

        self.stdout.write(
            self.style.SUCCESS(f'Очистка завершена. Удалено файлов: {deleted_count}')
        )
```

Запустить:
```powershell
python manage.py cleanup_images
```

---

## 14. Git и финальная сдача

### Шаг 14.1 — Инициализировать репозиторий

```powershell
git init
git config user.email "student@exam.ru"
git config user.name "Student"
```

### Шаг 14.2 — Создать .gitignore

Создать `.gitignore`:
```
.venv/
__pycache__/
*.pyc
*.pyo
.env
media/
*.sqlite3
```

### Шаг 14.3 — Первый коммит и дальнейшие коммиты

```powershell
# Первый коммит — структура проекта
git add manage.py pyproject.toml config/ core/ static/
git commit -m "initial commit"

# После каждого модуля делать коммит
git add .
git commit -m "module 1: add models and migrations"

git add .
git commit -m "module 1: add csv import script"

git add .
git commit -m "module 2: add login view and templates"

git add .
git commit -m "module 2: add product list with highlighting"

git add .
git commit -m "module 3: add search filter sort"

git add .
git commit -m "module 3: add product form with pillow"

git add .
git commit -m "module 3: add product delete"

git add .
git commit -m "module 4: add orders section"
```

### Шаг 14.4 — Привязать удалённый репозиторий и запушить

```powershell
# URL репозитория скажут на экзамене
git remote add origin https://github.com/USERNAME/REPONAME.git
git branch -M main
git push -u origin main
```

### Шаг 14.5 — Сохранить SQL-скрипт БД

```powershell
# Только схема (для сдачи)
& "C:\Program Files\PostgreSQL\16\bin\pg_dump.exe" -U postgres -s shoe_store > schema.sql

# Полный дамп с данными
& "C:\Program Files\PostgreSQL\16\bin\pg_dump.exe" -U postgres shoe_store > full_dump.sql

# Добавить в репозиторий
git add schema.sql full_dump.sql
git commit -m "add database dump"
git push
```

---

## 15. Чеклист перед сдачей

### Модуль 1 (10 баллов)
- [ ] БД создана в PostgreSQL (3НФ, ссылочная целостность)
- [ ] ER-диаграмма экспортирована в PDF (таблицы, связи, атрибуты, ключи)
- [ ] CSV данные загружены через `python manage.py import_data`
- [ ] SQL-скрипт сохранён (`schema.sql`)

### Модуль 2 (15 баллов)
- [ ] Блок-схема алгоритма в PDF (по ГОСТ 19.701-90)
- [ ] Страница входа — первое что видит пользователь
- [ ] Кнопка "Войти как гость" работает
- [ ] Авторизация по логину/паролю из БД работает
- [ ] ФИО пользователя отображается в правом верхнем углу
- [ ] Кнопка "Выйти" работает
- [ ] Список товаров показывается для всех ролей
- [ ] Фото товара или заглушка `picture.png`
- [ ] Подсветка: скидка >15% → `#2E8B57`
- [ ] Подсветка: нет на складе → голубой
- [ ] Цена перечёркнута красным + итоговая чёрным при скидке
- [ ] Шрифт Times New Roman
- [ ] Цвета: белый / `#7FFF00` / `#00FA9A`
- [ ] Логотип на главной форме (не искажён)
- [ ] Иконка приложения установлена
- [ ] Скриншоты работы в docx файле

### Модуль 3 (24 балла)
- [ ] Кнопка "Назад" на всех страницах
- [ ] Заголовки на каждой странице соответствуют назначению
- [ ] Обработка ошибок с информативными сообщениями
- [ ] Комментарии в коде в нужных местах
- [ ] Поиск в реальном времени (по всем текстовым полям)
- [ ] Фильтр по поставщику (первый элемент "Все поставщики")
- [ ] Сортировка по количеству (↑ и ↓)
- [ ] Поиск + фильтр работают совместно
- [ ] Сортировка сохраняется при поиске/фильтре
- [ ] Форма добавления товара (только администратор)
- [ ] Форма редактирования (клик по товару, администратор)
- [ ] Все поля загружаются при редактировании
- [ ] ID: не показывается при добавлении, read-only при редактировании
- [ ] Загрузка фото — ресайз 300×200 через Pillow
- [ ] Старое фото удаляется при замене
- [ ] Нельзя открыть два окна редактирования одновременно
- [ ] Удаление товара: нельзя удалить если есть в заказах
- [ ] Список обновляется после добавления/редактирования/удаления

### Модуль 4 (23 балла)
- [ ] Кнопка "Заказы" у менеджера и администратора
- [ ] Список заказов по макету (артикул, статус, адрес, дата заказа / дата доставки)
- [ ] Форма добавления заказа (только администратор)
- [ ] Форма редактирования заказа
- [ ] Удаление заказа
- [ ] Список обновляется после изменений

### Вариативная часть (25 баллов)
- [ ] Management-команда `import_data.py` работает
- [ ] `{% csrf_token %}` во всех POST-формах
- [ ] Management-команда `cleanup_images.py` удаляет неиспользуемые фото
- [ ] Pillow: ресайз изображений до 300×200
- [ ] Проект работает на Django (pyproject.toml с зависимостями)

### Git
- [ ] Репозиторий инициализирован
- [ ] Коммиты сделаны по модулям
- [ ] Код запушен в удалённый репозиторий
- [ ] Структура файлов (не архив!) загружена
- [ ] SQL-скрипт в репозитории

---

## БЫСТРЫЕ КОМАНДЫ (держать под рукой на экзамене)

```powershell
# Активировать venv
.venv\Scripts\activate

# Запустить сервер
python manage.py runserver

# Миграции
python manage.py makemigrations
python manage.py migrate

# Импорт данных
python manage.py import_data

# Очистка фото
python manage.py cleanup_images

# Дамп БД
& "C:\Program Files\PostgreSQL\16\bin\pg_dump.exe" -U postgres shoe_store > schema.sql

# Git
git add .
git commit -m "описание"
git push
```

---

*Инструкция составлена для демоэкзамена КОД 09.02.07-2-2026, ГИА ДЭ ПУ.*  
*Стек: Python 3.13 · Django · PostgreSQL · UV · VS Code · Windows*