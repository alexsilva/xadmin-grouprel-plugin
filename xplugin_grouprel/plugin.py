import inspect

from django.conf import settings
from django.contrib.auth.models import Group
from django.template.loader import render_to_string
from django.utils.encoding import force_text
from django.utils.translation import ugettext as _
from xadmin import site
from xadmin.plugins.utils import get_context_dict
from xadmin.views import BaseAdminPlugin

from xplugin_grouprel.views import GroupRelDataView, ObjGroupAddView, ObjectDeleteSelected


class GroupRelPlugin(BaseAdminPlugin):
    """Plugin that adds a table with model data related to the group"""
    template_table_ajax = 'xplugin-grouprel/inline-tabular-ajax.html'

    group_m2m_relation = None

    def init_request(self, object_id, *args, **kwargs):
        model = getattr(self.admin_view, "model", None)
        self.group_m2m_relation = getattr(self.admin_view, "group_m2m_relation",
                                          self.group_m2m_relation)

        if inspect.isclass(self.group_m2m_relation):
            self.group_m2m_relation = self.group_m2m_relation(self)

        return bool(self.group_m2m_relation is not None
                    and inspect.isclass(model)
                    and issubclass(model, Group))

    def get_context(self, context):
        """Context from table template"""
        context['opts'] = self.group_m2m_relation.opts
        context['ajax_table_url'] = self.admin_view.get_admin_url(
            "grouprel-dataview",
            app_label=self.group_m2m_relation.opts.app_label,
            model_name=self.group_m2m_relation.opts.model_name,
            pk=self.admin_view.org_obj.pk
        )

        model = self.group_m2m_relation.get_model()
        context['table_object_add'] = {
            'url': self.admin_view.get_model_url(model, "add"),
            'title': _('Add %s') % force_text(model._meta.verbose_name),
            'refresh_url': self.admin_view.get_admin_url("grouprel-groupobj-add",
                                                         pk=self.admin_view.org_obj.pk)
        }
        context['table_object_delete'] = {
            'url': self.admin_view.get_admin_url("grouprel-groupobj-delete"),
            'title': _("Remove all selected %s") % force_text(model._meta.verbose_name_plural),
        }
        context['table'] = dict(
            instance=self.group_m2m_relation,
            columns=self.group_m2m_relation.columns
        )
        return context

    def block_after_fieldsets(self, context, nodes, *args, **kwargs):
        html = render_to_string(
            self.template_table_ajax,
            context=get_context_dict(context))
        return nodes.append(html)

    def get_media(self, media):
        media.add_css({
            'screen': (
                settings.STATIC_URL + "xplugin-grouprel/css/dataTables.bootstrap.min.css",
                settings.STATIC_URL + "xplugin-grouprel/css/select.bootstrap.min.css",
                settings.STATIC_URL + "xplugin-grouprel/css/styles.css",
            )
        })
        media.add_js((
            settings.STATIC_URL + "xplugin-grouprel/js/jquery.dataTables.min.js",
            settings.STATIC_URL + "xplugin-grouprel/js/dataTables.bootstrap.min.js",
            settings.STATIC_URL + "xplugin-grouprel/js/dataTables.buttons.min.js",
            settings.STATIC_URL + "xplugin-grouprel/js/dataTables.select.min.js",
            settings.STATIC_URL + "xplugin-grouprel/js/select.bootstrap.min.js",
            settings.STATIC_URL + "xplugin-grouprel/js/grouprel.plugin.quick-form.js",
            settings.STATIC_URL + "xplugin-grouprel/js/group.table.handler.js",
        ))
        return media


site.register_view(r'^table/obj/(?P<pk>\d+)/add', ObjGroupAddView,
                   name='grouprel-groupobj-add')

site.register_view(r'^table/obj/delete/$', ObjectDeleteSelected,
                   name='grouprel-groupobj-delete')

site.register_view(r'^table/(?P<app_label>\w+)/(?P<model_name>\w+)/(?P<pk>\d+)',
                   GroupRelDataView,
                   name='grouprel-dataview')
