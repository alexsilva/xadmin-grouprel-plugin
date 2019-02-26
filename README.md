xadmin plugin that displays users related to groups in the edit screen. 
It is especially useful when the user number is extremely large. 
User are paginated and loaded with ajax.

Install
-
`python -m pip install git+https://github.com/alexsilva/xadmin-grouprel-plugin.git@master`

Setup
-

Add the app to installed-apps: `xplugin_grouprel`

Register the plugin:
```
from xplugin_grouprel.plugin import GroupRelPlugin
from xadmin import site

site.register_plugin(GroupRelPlugin, UpdateAdminView)
```

In the `adminx.py` script, implement the table interface:
```
from xplugin_grouprel import GroupRelatedModel

class GroupRelatedModelImpl(GroupRelatedModel):
    # model related to the group
    model = User
    
    # Fields that will appear in the data table
    fields = (
        'resolve_field_user_pk',
        'username',
        'email'
    )
    
    # this is a custom field
    def resolve_field_user_pk(self, instance):
        return instance.pk
    resolve_field_user_pk.verbose_name = u"hidden-user-pk"
    resolve_field_user_pk.datatable_visible = False
    resolve_field_user_pk.datatable_searchable = False
    resolve_field_user_pk.datatable_orderable = False
    resolve_field_user_pk.admin_order_field = "id"
```

In the admin model, configure the implemented class:
```
from xplugin_grouprel.plugin import GroupRelPlugin
from django.contrib.auth.models import Group
from xadmin import site

class GroupAdmin(object):
    # Activate the plugin in the group admin model
    group_rel_model = GroupRelatedModelImpl
    

# need to register the group again for the plugin to be activated.
site.unregister(Group)
site.register(Group, GroupAdmin)
```
