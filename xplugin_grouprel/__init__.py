# coding=utf-8
from django.utils.functional import cached_property
from django.db import models
import collections


class GroupRelatedModel(object):
    """interface class"""
    model = None  # model related to the group
    fields = ()

    def __init__(self, admin_view=None):
        self.admin_view = admin_view

    @cached_property
    def opts(self):
        return self.model._meta

    def queryset(self):
        """main queryset"""
        return self.model.objects.all()

    def get_model(self):
        return self.model

    @staticmethod
    def get_group_model():
        from django.contrib.auth.models import Group
        return Group

    @cached_property
    def map_fields(self):
        fields = collections.OrderedDict()
        for field_name in self.fields:
            if hasattr(self, field_name):
                field = getattr(self, field_name)
                field = field.admin_order_field
            else:
                field = field_name
            fields[field] = field_name
        return fields

    @cached_property
    def columns(self):
        """Returns a list with verbose_name of the configured fields"""
        names = []
        fields = self.map_fields
        for index, column in enumerate(fields.keys()):
            column_val = fields[column]
            try:
                field, db_column = column_val.split("__")
                field = self.opts.get_field(field)
            except ValueError:
                field = db_column = None

            if field is None and hasattr(self, column_val):
                field = getattr(self, column_val)
            elif db_column is not None and isinstance(field, models.ForeignKey):
                field = field.rel.to._meta.get_field(db_column)
            else:
                field = self.opts.get_field(column)

            datatable_config = dict(getattr(field, 'datatable_config', {}))
            datatable_config.setdefault('searchable', True)
            datatable_config.setdefault('orderable', True)
            datatable_config.setdefault('visible', True)
            datatable_config.setdefault('className', None)
            datatable_config.setdefault('checkboxes', False)
            datatable_config.setdefault('index', index)

            names.append({
                'verbose_name': getattr(field, "verbose_name", column),
                "queryset": {
                    "search_term": getattr(field, 'queryset_search_term', False),
                    'name': column,
                },
                # datatable configuration
                'datatable': datatable_config
            })
        return names

