import six
from django.apps import apps
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied, ValidationError
from django.utils.html import escape

try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils.translation import gettext as _
from django_datatables_view.base_datatable_view import BaseDatatableView
from xadmin.plugins.actions import DeleteSelectedAction
from xadmin.views import BaseAdminView, CommAdminView
import functools


class ObjectDeleteSelected(DeleteSelectedAction):
    delete_selected_confirmation_template = "xplugin-grouprel/model-delete-selected-confirm.html"
    delete_selected_option = '_selected_action'

    def __init__(self, *args, **kwargs):
        admin_class = self.admin_site._registry.get(Group)

        table = admin_class.group_rel_model(self)
        self.model = table.get_model()

        super(ObjectDeleteSelected, self).__init__(*args, **kwargs)

    def post(self, request, **kwargs):
        selected = (request.POST.getlist(self.delete_selected_option) or
                    request.POST.getlist(self.delete_selected_option + '[]'))
        queryset = self.queryset().filter(pk__in=selected)
        response = self.do_action(queryset)
        if response is None:
            response = JsonResponse({
                'result': 'success'
            })
        return response


class ObjGroupAddView(BaseAdminView):

    def get(self, request, **kwargs):
        """Performs the operation of adding an object to the group"""
        try:
            object_id = request.GET['obj_id']
        except KeyError:
            raise PermissionDenied

        admin_class = self.admin_site._registry.get(Group)
        table = admin_class.group_rel_model(self)
        model = table.get_model()

        # check add perm
        if not self.has_model_perm(model, 'add', self.request.user):
            raise PermissionDenied

        try:
            object_id = model._meta.pk.to_python(object_id)
        except ValidationError:
            raise PermissionDenied

        group = Group.objects.get(pk=kwargs['pk'])

        # Adds the group to the object
        obj = model.objects.get(pk=object_id)
        obj.groups.add(group)

        return HttpResponse('success')


class AjaxObjsGroupRemove(CommAdminView):

    def __init__(self, *args, **kwargs):
        super(AjaxObjsGroupRemove, self).__init__(*args, **kwargs)

        admin_class = self.admin_site._registry.get(Group)

        self.table = admin_class.group_rel_model(self)

    def get_context(self):
        context = super(AjaxObjsGroupRemove, self).get_context()
        context['group'] = dict(pk=self.kwargs['pk'])
        return context

    def post(self, request, **kwargs):
        objs = (request.POST.getlist("objs") or
                request.POST.getlist("objs" + '[]'))
        model = self.table.get_model()
        if not self.has_model_perm(model, 'change', self.request.user):
            raise PermissionDenied
        if not objs:
            return JsonResponse({
                'result': 'fail',
                'error': _('Select %(objs)s before send data') % {
                    'objs': model._meta.verbose_name_plural}
            })
        context = self.get_context()
        queryset = model.objects.filter(pk__in=objs)
        if request.POST.get('post'):
            group_model = self.table.get_group_model()
            group = group_model.objects.get(pk=self.kwargs['pk'])
            for obj in queryset:
                obj.groups.remove(group)
            return JsonResponse({
                'result': 'success'
            })
        else:
            context['objs'] = queryset
        return render(request, "xplugin-grouprel/ajax-objs-remove.html", context=context)


class AjaxTableObjsGroupView(CommAdminView):
    """Displays a table of data related to the group in a modal"""
    def __init__(self, *args, **kwargs):
        super(AjaxTableObjsGroupView, self).__init__(*args, **kwargs)

        admin_class = self.admin_site._registry.get(Group)

        self.table = admin_class.group_rel_model(self)

    def get_context(self):
        """Context from table template"""
        context = super(AjaxTableObjsGroupView, self).get_context()
        context['opts'] = self.table.opts
        model = self.table.get_model()
        group_model = self.table.get_group_model()
        context['box_title'] = _("Add %(objs)s to %(group)s") % {
            'objs': model._meta.verbose_name_plural,
            'group': group_model._meta.verbose_name
        }
        context['table'] = dict(
            instance=self.table,
            columns=self.table.columns,
            id="group-rel-ajax-table"
        )
        context['inline_style'] = 'blank'
        context['prefix'] = context['table']['id']
        context['group'] = dict(pk=self.kwargs['pk'])
        context['ajax_table_url'] = self.get_admin_url(
            "grouprel-dataview",
            app_label=self.table.opts.app_label,
            model_name=self.table.opts.model_name,
            pk=self.kwargs['pk']
        )
        return context

    def get(self, request, **kwargs):
        context = self.get_context()
        return render(request, "xplugin-grouprel/ajax-table.html",
                      context=context)

    def post(self, request, **kwargs):
        model = self.table.get_model()
        if not self.has_model_perm(model, 'change', self.request.user):
            raise PermissionDenied
        objs = (request.POST.getlist("objs") or
                request.POST.getlist("objs[]"))
        if not objs:
            return JsonResponse({
                'result': 'fail',
                'error': _('Select %(objs)s before send data') % {
                    'objs': model._meta.verbose_name_plural}
            })
        group_model = self.table.get_group_model()
        group = group_model.objects.get(pk=self.kwargs['pk'])
        for obj in model.objects.filter(pk__in=objs):
            obj.groups.add(group)
        return JsonResponse({
            'result': 'success'
        })


class GroupRelDataView(BaseDatatableView, BaseAdminView):
    """Data view of the table datatable"""

    def __init__(self, *args, **kwargs):
        self.plugin_classes = []
        super(GroupRelDataView, self).__init__(*args, **kwargs)
        self.table = None
        self.map_fields = None

    def get_filter_method(self):
        return self.FILTER_ICONTAINS

    def filter_queryset(self, queryset, **kwargs):
        qs = super().filter_queryset(queryset, **kwargs)
        if not self.pre_camel_case_notation:
            search = self._querydict.get('search[value]', None)
            query = Q()
            if search:
                # Multiple column search
                chunks, filter_method = [], self.get_filter_method()
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
                                query |= Q(**{"{0[name]}__{1:s}".format(config, filter_method): chunk})
                qs |= queryset.filter(query)
        return qs

    def render_column(self, row, column):
        column_val = self.map_fields[column]
        table_column = getattr(self.table, column_val, None)
        obj = row
        try:
            field, db_column = column_val.split("__")
            field = self.table.opts.get_field(field)
        except ValueError:
            field = db_column = None

        # The column is a callable method or function.
        if field is None and table_column:
            value = table_column(obj)
            try:
                field = getattr(table_column, "admin_order_field")
            except models.FieldDoesNotExist:
                field = self.table.opts.get_field(column)
        elif isinstance(field, models.ForeignKey):
            value = functools.reduce(lambda x, y: getattr(x, y), [obj, field.name, db_column])
        else:
            value = str(getattr(obj, column))
            field = self.table.opts.get_field(column)

        if getattr(table_column, "link_display", False) and value and field and \
                self.has_model_perm(self.table.get_model(), 'change', self.request.user):
            field_name = getattr(obj, field if isinstance(field, six.string_types) else field.name)
            change_url = self.get_model_url(self.table.get_model(), 'change', field_name)
            return '<a href="{0}">{1}</a>'.format(change_url, escape(value))
        return value

    def initialize(self, *args, **kwargs):
        self.model = apps.get_model(self.kwargs['app_label'], self.kwargs['model_name'])

        admin_class = self.admin_site._registry.get(Group)

        self.table = admin_class.group_rel_model(self)
        self.map_fields = self.table.map_fields
        self.columns = list(self.map_fields.keys())

        return super(GroupRelDataView, self).initialize(*args, **kwargs)

    def get_initial_queryset(self):
        if not self.has_model_perm(self.table.get_model(), 'view',
                                   self.request.user):
            raise PermissionDenied
        queryset = self.table.queryset()
        if self.request.GET.get('reversed'):
            queryset = queryset.exclude(groups__pk=self.kwargs['pk'])
        else:
            queryset = queryset.filter(groups__pk=self.kwargs['pk'])
        return queryset
