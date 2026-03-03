from django.utils.translation import gettext_lazy as _

MODULE_ID = 'tables'
MODULE_NAME = _('Tables')
MODULE_VERSION = '2.0.0'

MENU = {
    'label': _('Tables'),
    'icon': 'material:table_restaurant',
    'order': 20,
}

NAVIGATION = [
    {'id': 'floor_plan', 'label': _('Floor Plan'), 'icon': 'map-outline', 'view': ''},
    {'id': 'zones', 'label': _('Zones'), 'icon': 'layers-outline', 'view': 'zones'},
    {'id': 'tables', 'label': _('Tables'), 'icon': 'grid-outline', 'view': 'tables'},
    {'id': 'sessions', 'label': _('Sessions'), 'icon': 'time-outline', 'view': 'sessions'},
    {'id': 'settings', 'label': _('Settings'), 'icon': 'settings-outline', 'view': 'settings'},
]

PERMISSIONS = [
    'tables.view_zone',
    'tables.add_zone',
    'tables.change_zone',
    'tables.delete_zone',
    'tables.view_table',
    'tables.add_table',
    'tables.change_table',
    'tables.delete_table',
    'tables.view_tablesession',
    'tables.add_tablesession',
    'tables.change_tablesession',
    'tables.delete_tablesession',

    'tables.manage_settings',
]

ROLE_PERMISSIONS = {
    "admin": ["*"],
    "manager": [
        "add_table",
        "add_tablesession",
        "add_zone",
        "change_table",
        "change_tablesession",
        "change_zone",
        "view_table",
        "view_tablesession",
        "view_zone",
    ],
    "employee": [
        "add_zone",
        "view_table",
        "view_tablesession",
        "view_zone",
    ],
}
