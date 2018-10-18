import inspect

from django.conf import settings
from django.contrib.auth.models import Group
from django.template.loader import render_to_string
from xadmin.plugins.utils import get_context_dict
from xadmin.views import BaseAdminPlugin


class GroupRelPlugin(BaseAdminPlugin):
    template_table_ajax = 'xplugin-grouprel/inline-tabular-ajax.html'

    group_related_model = None

    def init_request(self, object_id, *args, **kwargs):
        model = getattr(self.admin_view, "model", None)
        self.group_related_model = getattr(self.admin_view, "group_related_model",
                                           self.group_related_model)
        return self.group_related_model and inspect.isclass(model) and issubclass(model, Group)

    def get_context(self, context):
        context['opts'] = self.group_related_model._meta
        return context

    def block_after_fieldsets(self, context, nodes, *args, **kwargs):
        html = render_to_string(
            self.template_table_ajax,
            context=get_context_dict(context))
        return nodes.append(html)

    def get_media(self, media):
        media.add_js((
            settings.STATIC_URL + "/xplugin-grouprel/js/jquery.dataTables.min.js",
        ))
        return media
