import inspect

from django.conf import settings
from django.template.loader import render_to_string
from django.utils.encoding import force_text
from django.utils.translation import ugettext as _
from xadmin import site
from xadmin.plugins.utils import get_context_dict
from xadmin.views import BaseAdminPlugin

from xplugin_grouprel.views import (
    GroupRelDataView,
    AjaxObjsGroupRemove,
    AjaxTableObjsGroupView
)


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
                    and issubclass(model, self.group_m2m_relation.get_group_model())
                    and self.has_model_perm(self.group_m2m_relation.get_model(), 'view',
                                            self.admin_view.request.user))

    def get_context(self, context):
        """Context from table template"""
        context['opts'] = self.group_m2m_relation.opts
        context['table'] = dict(
            instance=self.group_m2m_relation,
            columns=self.group_m2m_relation.columns,
            id="group-rel-table"
        )
        context['ajax_table_url'] = self.admin_view.get_admin_url(
            "grouprel-dataview",
            app_label=self.group_m2m_relation.opts.app_label,
            model_name=self.group_m2m_relation.opts.model_name,
            pk=self.admin_view.org_obj.pk
        )
        model = self.group_m2m_relation.get_model()
        context['table_object_add'] = {
            'url': self.admin_view.get_admin_url("grouprel-ajax-table",
                                                 pk=self.admin_view.org_obj.pk),
            'title': _('Add %s') % force_text(model._meta.verbose_name)
        }
        context['table_object_remove'] = {
            'url': self.admin_view.get_admin_url("grouprel-objs-remove",
                                                 pk=self.admin_view.org_obj.pk),
            'title': _("Remove all selected %s ?") % force_text(model._meta.verbose_name_plural),
        }
        return context

    def block_after_fieldsets(self, context, nodes, *args, **kwargs):
        html = render_to_string(
            self.template_table_ajax,
            context=get_context_dict(context))
        return nodes.append(html)

    def block_extrabody(self, context, nodes, *args, **kwargs):
        html = render_to_string(
            "xplugin-grouprel/table-config.html",
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
            settings.STATIC_URL + "xplugin-grouprel/js/group.table.plugin.js",
        ))
        return media


site.register_view(r'^table/ajax/(?P<pk>\d+)/$', AjaxTableObjsGroupView,
                   name='grouprel-ajax-table')

site.register_view(r'^table/objs/(?P<pk>\d+)/remove/$', AjaxObjsGroupRemove,
                   name='grouprel-objs-remove')

site.register_view(r'^table/(?P<app_label>\w+)/(?P<model_name>\w+)/(?P<pk>\d+)',
                   GroupRelDataView,
                   name='grouprel-dataview')
