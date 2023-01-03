from abc import ABC
from typing import Type, List

from django.db.models import Model, Q
from rest_framework import serializers

from people.utils.variable_res_date import VariableResolutionDateField, VariableResolutionDateSerializerField


def get_updatable_fields(model_cls: Type[Model]):
    return [
        field
        for field in model_cls._meta.concrete_fields
        if not getattr(field, 'primary_key', False)
    ]


class BulkListSerializer(serializers.ListSerializer, ABC):
    model_cls = None

    def get_model_data_pairs(self, validated_data: List[dict], existing_instances: List[Model]):
        for data in validated_data:
            instance = next(iter([x for x in existing_instances if x.pk == data['id']]), __default=None)
            yield data, instance

    def get_existing_filter_expr(self, validated_data: List[dict]):
        return Q(pk__in=[x['id'] for x in validated_data])

    def save(self, **kwargs):
        validated_data = [{**attrs, **kwargs} for attrs in self.validated_data]

        existing_for_update = self.model_cls.objects.filter(self.get_existing_filter_expr(validated_data))

        for_update = []
        for_create = []
        for update_content, opt_instance in self.get_model_data_pairs(validated_data, existing_for_update):
            if not opt_instance:
                for_create.append(self.model_cls(**update_content))
            else:
                for key, value in update_content.items():
                    setattr(opt_instance, key, value)
                for_update.append(opt_instance)

        created = self.model_cls.objects.bulk_create(for_create, batch_size=500)
        updated = self.model_cls.objects.bulk_update(
            for_update,
            batch_size=500,
            fields=[field.name for field in get_updatable_fields(self.model_cls)]
        )

        return created, updated


class ModelSerializer(serializers.ModelSerializer):
    serializer_field_mapping = {
        VariableResolutionDateField: VariableResolutionDateSerializerField,
        **serializers.ModelSerializer.serializer_field_mapping
    }
