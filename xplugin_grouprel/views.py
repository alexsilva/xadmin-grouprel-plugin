from django.apps import apps
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils.translation import ugettext as _
from django_datatables_view.base_datatable_view import BaseDatatableView
from xadmin.plugins.actions import DeleteSelectedAction
from xadmin.views import BaseAdminView, CommAdminView


class ObjectDeleteSelected(DeleteSelectedAction):
    delete_selected_confirmation_template = "xplugin-grouprel/model-delete-selected-confirm.html"
    delete_selected_option = '_selected_action'

    def __init__(self, *args, **kwargs):
        admin_class = self.admin_site._registry.get(Group)

        table = admin_class.group_m2m_relation()
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
        table = admin_class.group_m2m_relation()
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

        self.table = admin_class.group_m2m_relation()

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

        self.table = admin_class.group_m2m_relation()

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
        context['ajax_table_url'] = reverse(
            '%s:%s' % (self.admin_site.app_name, "grouprel-dataview"),
            kwargs=dict(app_label=self.table.opts.app_label,
                        model_name=self.table.opts.model_name,
                        pk=self.kwargs['pk'])
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
                request.POST.getlist("objs" + '[]'))
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

        self.table = admin_class.group_m2m_relation()
        self.map_fields = self.table.map_fields
        self.columns = self.map_fields.keys()
        column = self.table.get_first_column()
        if column is not None:
            self.column_first = self.columns[column['datatable']['index']]
        else:
            self.column_first = column
        return super(GroupRelDataView, self).initialize(*args, **kwargs)

    def get_initial_queryset(self):
        if not self.has_model_perm(self.table.get_model(), 'view',
                                   self.request.user):
            raise PermissionDenied
        queryset = self.table.queryset()
        if self.request.GET.get('reversed'):
            queryset = queryset.filter(~Q(group__pk=self.kwargs['pk']))
        else:
            queryset = queryset.filter(group__pk=self.kwargs['pk'])
        return queryset
