from django.apps import apps
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.db import models
from django.db.models import Q
from xadmin.views import BaseAdminView

from django_datatables_view.base_datatable_view import BaseDatatableView


class GroupRelDataView(BaseDatatableView, BaseAdminView):
    """Data view of the table datatable"""

    def __init__(self, *args, **kwargs):
        self.plugin_classes = []
        super(GroupRelDataView, self).__init__(*args, **kwargs)
        self.column_first = None
        self.table = None
        self.map_fields = None

    def get_filter_method(self):
        return self.FILTER_ICONTAINS

    def get_filter_query(self):
        search = self._querydict.get('search[value]', None)
        query = Q()
        if search:
            # Multiple column search
            filter_method = self.get_filter_method()
            chunks = []
            for s in search.split(" ", 4):
                s = s.strip()
                if len(s) == 0:
                    continue
                chunks.append(s)
            if len(chunks) > 0:
                for column in self.table.columns:
                    config = column['queryset']
                    if config['search_term']:
                        for chunk in chunks:
                            chunk = chunk.strip()
                            if not chunk:
                                continue
                            query |= Q(**{"{0[name]}__{1:s}".format(config, filter_method): chunk})
        return query

    def render_column(self, row, column):
        column_val = self.map_fields[column]
        obj = row
        try:
            field, db_column = column_val.split("__")
            field = self.table.opts.get_field(field)
        except ValueError:
            field = db_column = None

        if field is None and hasattr(self.table, column_val):
            value = getattr(self.table, column_val)(obj)
            try:
                field = self.table.opts.get_field(column)
            except models.FieldDoesNotExist:
                field = None
        elif isinstance(field, models.ForeignKey):
            value = reduce(lambda x, y: getattr(x, y), [obj, field.name, db_column])
        else:
            value = unicode(getattr(obj, column))
            field = self.table.opts.get_field(column)

        if self.column_first == column and value and field and isinstance(field, models.ForeignKey):
            change_url = self.get_model_url(field.rel.to, 'change',
                                            getattr(obj, field.name).pk)
            return u'<a href="%s">%s</a>' % (change_url, value)
        return value

    def initialize(self, *args, **kwargs):
        self.model = apps.get_model(self.kwargs['app_label'], self.kwargs['model_name'])

        admin_class = self.admin_site._registry.get(Group)

        self.table = admin_class.group_related_table()
        self.map_fields = self.table.map_fields
        self.columns = self.map_fields.keys()
        try:
            self.column_first = self.columns[0]
        except IndexError:
            self.column_first = None
        return super(GroupRelDataView, self).initialize(*args, **kwargs)

    def get_initial_queryset(self):
        if not self.has_model_perm(self.model, 'view', self.request.user):
            raise PermissionDenied
        queryset = self.table.queryset()
        queryset = queryset.filter(group__pk=self.kwargs['pk'])
        return queryset
