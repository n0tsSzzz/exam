from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from core.models import Product


class Command(BaseCommand):
    help = "Удаляет файлы media/products, которые не используются товарами."

    def handle(self, *args, **options):
        products_dir = Path(settings.MEDIA_ROOT) / "products"
        products_dir.mkdir(parents=True, exist_ok=True)

        # В БД хранится путь products/file.jpg, а на диске сравниваем только имя файла.
        used_files = {
            Path(photo).name
            for photo in Product.objects.exclude(photo="").values_list("photo", flat=True)
            if photo
        }

        deleted = 0
        for file_path in products_dir.iterdir():
            if file_path.name == ".gitkeep":
                continue
            if file_path.is_file() and file_path.name not in used_files:
                file_path.unlink()
                deleted += 1

        self.stdout.write(self.style.SUCCESS(f"Удалено файлов: {deleted}"))
