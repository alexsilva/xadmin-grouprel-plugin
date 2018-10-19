from django.apps import apps
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django_datatables_view.base_datatable_view import BaseDatatableView
from xadmin.views import BaseAdminView


class GroupRelDataView(BaseDatatableView, BaseAdminView):
    """Data view of the table datatable"""

    def __init__(self, *args, **kwargs):
        self.plugin_classes = []
        super(GroupRelDataView, self).__init__(*args, **kwargs)
        self.column_first = None
        self.table = None

    def render_column(self, row, column):
        obj = row
        try:
            field, _column = column.split("__")
        except ValueError:
            field, _column = None, column

        if field is not None:
            value = reduce(lambda x, y: getattr(x, y), [obj, field, _column])
            field = self.table.opts.get_field(field)
        else:
            value = getattr(obj, column)

        if self.column_first == column and value and field is not None:
            change_url = self.get_model_url(field.rel.to, 'change',
                                            getattr(obj, field.name).pk)
            return u'<a href="%s">%s</a>' % (change_url, value)
        return value

    def initialize(self, *args, **kwargs):
        self.model = apps.get_model(self.kwargs['app_label'], self.kwargs['model_name'])

        admin_class = self.admin_site._registry.get(Group)

        self.table = admin_class.group_related_table()

        self.columns = self.table.fields

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
