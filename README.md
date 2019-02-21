# xadmin-grouprel-plugin
Xadmin plugin that displays user related to a group (datatable)

Setup
-

Add the app to installed-apps: `xplugin_grouprel`

Register the plugin:
```
from xplugin_grouprel.plugin import GroupRelPlugin

site.register_plugin(GroupRelPlugin, UpdateAdminView)
```

In the adminx script, implement the table interface:
```
from xplugin_grouprel import GroupM2MRelation

class GroupM2MRelationImpl(GroupM2MRelation):
    # modelo intermediate group
    through = User.groups.through
    
    # model related to the group
    model = User
    
    # Fields that will appear in the data table
    fields = (
        'user__username',
        'user__email'
    )
```

In the admin model, configure the implemented class:
```
from xplugin_grouprel.plugin import GroupRelPlugin

class ModelGroupAdmin(object):
    # Activate the plugin in the group admin model
    group_m2m_relation = GroupM2MRelationImpl
```
