import inspect
import json
import os

from django.conf import settings
from django.core.management import BaseCommand

from people import models
from people.models import ExportableEnum
from people.utils import snake_to_camel


def enum_values_to_json(cls):
    return {
        snake_to_camel(name): value
        for name, value in zip(cls.names, cls.values)
    }


def enum_labels_to_json(cls):
    return {
        value: str(label) for value, label in zip(cls.values, cls.labels)
    }


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        classes = list(map(lambda x: x[1], inspect.getmembers(models, lambda x: inspect.isclass(x))))
        classes += [cls_attr for cls in classes for cls_attr in cls.__dict__.values() if inspect.isclass(cls_attr)]
        enum_classes = list(filter(lambda x: issubclass(x, ExportableEnum) and x != ExportableEnum, classes))

        enums = {cls.__name__: enum_values_to_json(cls) for cls in enum_classes}
        labels = {cls.__name__: enum_labels_to_json(cls) for cls in enum_classes}

        with open(os.path.join(settings.BASE_DIR, 'people', 'static', 'people', 'js', 'graph_enums.js'), 'w') as f:
            f.write('enums = {};\n'.format(json.dumps(enums, indent=4)))
            f.write('labels = {};\n'.format(json.dumps(labels, indent=4)))
