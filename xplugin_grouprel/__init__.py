# coding=utf-8
from django.utils.functional import cached_property
import collections


class GroupRelatedTable(object):
    """interface class"""
    model = None
    fields = ()

    def __init__(self, plugin=None):
        self.plugin = plugin

    @cached_property
    def opts(self):
        return self.model._meta

    def queryset(self):
        """main queryset"""
        return self.model.objects.all()

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
        for index, field_name in enumerate(self.fields):
            try:
                model, field_name = field_name.split("__")
            except ValueError:
                model, field_name = None, field_name
            if hasattr(self, field_name):
                field = getattr(self, field_name)
            elif model is not None:
                model = self.opts.get_field(model).rel.to
                field = model._meta.get_field(field_name)
            else:
                field = self.opts.get_field(field_name)
            names.append({
                'verbose_name': (getattr(field, "verbose_name", field_name) or field_name),
                # datatable configuration
                'datatable': {
                    'searchable': getattr(field, 'datatable_searchable', True),
                    'orderable': getattr(field, 'datatable_orderable', True),
                    'visible': getattr(field, 'datatable_visible', True),
                    'index': index
                }
            })
        return names

