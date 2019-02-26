# coding=utf-8
from django.utils.functional import cached_property
from django.db import models
import collections


class GroupRelatedModel(object):
    """interface class"""
    model = None  # model related to the group
    fields = ()

    def __init__(self, plugin=None):
        self.plugin = plugin

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

    def get_first_column(self):
        for column in self.columns:
            # search the first visible column
            if column['datatable']['visible']:
                return column
        return None

    @cached_property
    def columns(self):
        """Returns a list with verbose_name of the configured fields"""
        names = []
        fields = self.map_fields
        for index, column in enumerate(fields.iterkeys()):
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
            names.append({
                'verbose_name': (getattr(field, "verbose_name", column) or column),
                "queryset": {
                    "search_term": getattr(field, 'queryset_search_term', False),
                    'name': column,
                },
                # datatable configuration
                'datatable': {
                    'searchable': getattr(field, 'datatable_searchable', True),
                    'orderable': getattr(field, 'datatable_orderable', True),
                    'visible': getattr(field, 'datatable_visible', True),
                    'className': getattr(field, 'datatable_class_name', None),
                    'index': index
                }
            })
        return names

