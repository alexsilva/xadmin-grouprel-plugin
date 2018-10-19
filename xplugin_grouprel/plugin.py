import inspect

from django.conf import settings
from django.contrib.auth.models import Group
from django.template.loader import render_to_string
from xadmin import site
from xadmin.plugins.utils import get_context_dict
from xadmin.views import BaseAdminPlugin

from xplugin_grouprel.views import GroupRelDataView


class GroupRelPlugin(BaseAdminPlugin):
    """Plugin that adds a table with model data related to the group"""
    template_table_ajax = 'xplugin-grouprel/inline-tabular-ajax.html'

    group_related_table = None

    def init_request(self, object_id, *args, **kwargs):
        model = getattr(self.admin_view, "model", None)
        self.group_related_table = getattr(self.admin_view, "group_related_table",
                                           self.group_related_table)

        if inspect.isclass(self.group_related_table):
            self.group_related_table = self.group_related_table(self)

        return bool(self.group_related_table is not None
                    and inspect.isclass(model)
                    and issubclass(model, Group))

    def get_context(self, context):
        """Context from table template"""
        context['opts'] = self.group_related_table.opts
        context['table'] = dict(
            instance=self.group_related_table,
            columns=self.group_related_table.get_columns()
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
                settings.STATIC_URL + "xplugin-grouprel/css/styles.css",
            )
        })
        media.add_js((
            settings.STATIC_URL + "xplugin-grouprel/js/jquery.dataTables.min.js",
            settings.STATIC_URL + "xplugin-grouprel/js/dataTables.bootstrap.min.js",
            settings.STATIC_URL + "xplugin-grouprel/js/group.table.handler.js",
        ))
        return media


site.register_view(r'^table/(?P<app_label>\w+)/(?P<model_name>\w+)/',
                   GroupRelDataView,
                   name='grouprel-dataview')