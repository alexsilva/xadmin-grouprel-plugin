# xadmin-grouprel-plugin
Xadmin plugin that displays user related to a group (datatable)

Setup
-

Add the app to installed-apps: xplugin_grouprel

In the adminx script, implement the table interface.
```
from xplugin_grouprel import GroupRelatedTable

class GroupRelatedTableImpl(GroupRelatedTable):
    # Group related model
    model = User.groups.through
    
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
    group_related_table = GroupRelatedTableImpl
```
