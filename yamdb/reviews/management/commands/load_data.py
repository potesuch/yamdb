import csv
import os
from glob import glob

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models.fields.related import RelatedField
from reviews import models

STATIC_ROOT = settings.STATIC_ROOT


class Command(BaseCommand):
    """
    Класс команды Django для импорта данных из CSV файлов в соответствующие модели.
    """

    def add_arguments(self, parser):
        """
        Добавляет аргументы командной строки для команды.

        Args:
            parser (argparse.ArgumentParser): Парсер аргументов.
        """
        parser.add_argument('args', nargs='+', type=str)

    def handle(self, *args, **options):
        """
        Основной метод команды. Обрабатывает переданные аргументы и вызывает процесс импорта данных.

        Args:
            args (list): Список аргументов командной строки.
            options (dict): Словарь дополнительных опций.
        """
        csv_dict = self.get_csv_dict()
        for arg in args:
            self.process_csv_file(arg, csv_dict)

    def get_csv_dict(self):
        """
        Получает словарь соответствий моделей и CSV файлов.

        Returns:
            dict: Словарь, где ключи - имена моделей, значения - пути к CSV файлам.
        """
        data_path = os.path.join(STATIC_ROOT, 'data')
        csv_files = glob(os.path.join(data_path, '*.csv'))
        csv_dict = {}
        for csv_file in csv_files:
            csv_name = os.path.basename(csv_file).split('.')[0]
            model_name = self.get_model_name(csv_name)
            csv_dict[model_name] = csv_file
        return csv_dict

    def get_model_name(self, csv_name):
        """
        Преобразует имя CSV файла в имя модели.

        Args:
            csv_name (str): Имя CSV файла без расширения.

        Returns:
            str: Имя модели.
        """
        if '_' in csv_name:
            return ''.join(p.capitalize() for p in csv_name.split('_'))
        return csv_name.capitalize()

    def process_csv_file(self, arg, csv_dict):
        """
        Обрабатывает CSV файл и импортирует данные в соответствующую модель.

        Args:
            arg (str): Имя модели.
            csv_dict (dict): Словарь соответствий моделей и CSV файлов.
        """
        csv_file = csv_dict.get(arg)
        if csv_file:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                model = getattr(models, arg, None)
                if model:
                    self.populate_model_data(model, reader)
                else:
                    self.stdout.write(self.style.ERROR(
                        f'Модели {arg} не существует!'
                    ))
        else:
            self.stdout.write(self.style.ERROR(
                f'Файл с данными для {arg} не найден'
            ))

    def populate_model_data(self, model, reader):
        """
        Заполняет модель данными из CSV файла.

        Args:
            model (django.db.models.Model): Модель для заполнения.
            reader (csv.DictReader): Объект для чтения CSV данных.
        """
        mapping = {}
        data = {}
        fields = model._meta.get_fields()
        for field in fields:
            if isinstance(field, RelatedField):
                mapping[f'{field.name}_id'] = field.name
            else:
                mapping[field.name] = field.name
        for row in reader:
            for k, v in mapping.items():
                data[k] = row.get(v, row.get(k))
            for k, v in data.copy().items():
                if not v:
                    del data[k]
            self.create_model_instance(model, data)

    def create_model_instance(self, model, data):
        """
        Создает экземпляр модели с данными и сохраняет его в базу данных.

        Args:
            model (django.db.models.Model): Модель для заполнения.
            data (dict): Данные для заполнения модели.
        """
        obj = model(**data)
        obj.save()
        self.stdout.write(self.style.NOTICE(
            f'{data}'
        ))
        self.stdout.write(self.style.SUCCESS(
            f'Данные в {model.__name__} записаны.'
        ))
