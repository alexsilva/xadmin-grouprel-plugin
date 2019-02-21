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
from xadmin import site

class GroupAdmin(object):
    # Activate the plugin in the group admin model
    group_m2m_relation = GroupM2MRelationImpl
    

# need to register the group again for the plugin to be activated.
site.unregister(Group)
site.register(Group, GroupAdmin)
```
