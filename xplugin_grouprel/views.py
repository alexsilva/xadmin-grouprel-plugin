from django.apps import apps
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django_datatables_view.base_datatable_view import BaseDatatableView
from xadmin.views import BaseAdminView


class GroupRelDataView(BaseDatatableView, BaseAdminView):

    def __init__(self, *args, **kwargs):
        self.plugin_classes = []
        super(GroupRelDataView, self).__init__(*args, **kwargs)
        self.table = None

    def render_column(self, row, column):
        obj = row
        try:
            model, column = column.split("__")
        except ValueError:
            model, column = None, column

        if model is not None:
            value = reduce(lambda x, y: getattr(x, y), [obj, model, column])
        else:
            value = getattr(obj, column)

        if value and model and hasattr(model, 'get_absolute_url'):
            return '<a href="%s">%s</a>' % (model.get_absolute_url(), value)
        return value

    def initialize(self, *args, **kwargs):
        self.model = apps.get_model(self.kwargs['app_label'], self.kwargs['model_name'])

        admin_class = self.admin_site._registry.get(Group)

        self.table = admin_class.group_related_table()

        self.columns = self.table.fields

        return super(GroupRelDataView, self).initialize(*args, **kwargs)

    def get_initial_queryset(self):
        if not self.has_model_perm(self.model, 'view', self.request.user):
            raise PermissionDenied

        return self.table.queryset()
