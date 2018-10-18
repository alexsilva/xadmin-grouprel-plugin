# coding=utf-8
from django.utils.functional import cached_property


class GroupRelatedTable(object):
    """interface class"""
    model = None
    fields = ()

    def __init__(self, plugin):
        self.plugin = plugin

    @cached_property
    def opts(self):
        return self.model._meta

    def get_columns(self):
        """Returns a list with verbose_name of the configured fields"""
        names = []
        for field_name in self.fields:
            try:
                model, field_name = field_name.split("__")
            except ValueError:
                model, field_name = None, field_name

            if model is not None:
                model = self.opts.get_field(model).rel.to
                field = model._meta.get_field(field_name)
            else:
                field = self.opts.get_field(field_name)
            names.append(getattr(field, "verbose_name", field_name) or field_name)
        return names

