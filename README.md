# Демоэкзамен 09.02.07 ПУ

Учебный шаблон Django + PostgreSQL для проекта уровня ПУ: товары, роли, заказы, импорт CSV, CSRF и работа с изображениями через Pillow.

## Быстрый запуск на Windows

Вариант через `uv`, без активации `.venv`:

```powershell
uv sync
uv run python manage.py migrate
uv run python manage.py import_data --path import_data
uv run python manage.py runserver
```

Обычный вариант через `venv`:

```powershell
py -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

Создай базу PostgreSQL `demoexam_26`. В проекте используются простые учебные настройки: пользователь `postgres`, пароль `123456`, хост `localhost`, порт `5432`.

```powershell
python manage.py makemigrations
python manage.py migrate
python manage.py import_data --path import_data
python manage.py runserver
```

## Импорт CSV

Положи CSV-файлы в папку `import_data`. Если данные выдали в Excel `.xlsx`, сначала сохрани каждый лист как `CSV UTF-8`.

- `users.csv`
- `pickup_points.csv`
- `products.csv`
- `orders.csv`
- `user_import.csv`
- `Пункты выдачи_import.csv`
- `Tovar.csv`
- `Заказ_import.csv`

Запуск:

```powershell
python manage.py import_data
```

Для другой папки:

```powershell
python manage.py import_data --path "C:\path\to\import"
```

Очистка неиспользуемых фото:

```powershell
python manage.py cleanup_media
```

SQL-скрипт структуры базы для сдачи лежит в `database_schema.sql`.

## Роли

- `admin`: товары и заказы, полный CRUD
- `manager`: товары с поиском/фильтрацией/сортировкой, просмотр заказов
- `client`: только просмотр товаров
- гость: только просмотр товаров
