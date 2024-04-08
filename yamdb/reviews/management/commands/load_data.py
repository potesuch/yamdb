import os
import csv
from glob import glob
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models.fields.related import RelatedField
from reviews import models

STATIC_ROOT = settings.STATIC_ROOT


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('args', nargs='+', type=str)

    def handle(self, *args, **options):
        data_path = os.path.join(STATIC_ROOT, 'data')
        csv_files = glob(os.path.join(data_path, '*.csv'))
        csv_dict = {}
        for csv_file in csv_files:
            csv_name = os.path.basename(csv_file).split('.')[0]
            if '_' in csv_name:
                model_name = ''.join(
                    p.capitalize() for p in csv_name.split('_')
                )
            else:
                model_name = csv_name.capitalize()
            csv_dict[model_name] = csv_file
        for arg in args:
            csv_file = csv_dict.get(arg)
            if csv_file:
                with open(csv_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    model = getattr(models, arg, None)
                    if model:
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
                            self.stdout.write(self.style.NOTICE(
                                f'{data}'
                            ))
                            obj = model(**data)
                            obj.save()
                        self.stdout.write(self.style.SUCCESS(
                            f'Данные в {arg} записаны.'
                        ))
                    else:
                        self.stdout.write(self.style.ERROR(
                            f'Модели {arg} не сущетствует!'
                        ))
            else:
                self.stdout.write(self.style.ERROR(
                    f'Файла с данными для {arg} не найдено'
                ))
