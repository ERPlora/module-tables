"""AI tools for the Tables module."""
from assistant.tools import AssistantTool, register_tool


@register_tool
class ListZones(AssistantTool):
    name = "list_zones"
    description = "List table zones/areas (e.g., 'Terraza', 'Interior', 'Barra'). Returns name, table count, available tables."
    module_id = "tables"
    required_permission = "tables.view_zone"
    parameters = {
        "type": "object",
        "properties": {
            "is_active": {"type": "boolean", "description": "Filter by active status"},
        },
        "required": [],
        "additionalProperties": False,
    }

    def execute(self, args, request):
        from tables.models import Zone
        qs = Zone.objects.all()
        if 'is_active' in args:
            qs = qs.filter(is_active=args['is_active'])
        return {
            "zones": [
                {
                    "id": str(z.id),
                    "name": z.name,
                    "color": z.color,
                    "is_active": z.is_active,
                    "table_count": z.table_count,
                    "available_tables": z.available_tables,
                }
                for z in qs
            ]
        }


@register_tool
class CreateZone(AssistantTool):
    name = "create_zone"
    description = "Create a new table zone/area (e.g., 'Terraza', 'Sala VIP')."
    module_id = "tables"
    required_permission = "tables.add_zone"
    requires_confirmation = True
    parameters = {
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "Zone name"},
            "description": {"type": "string", "description": "Zone description"},
            "color": {"type": "string", "description": "Color class (e.g., 'primary', 'success')"},
            "sort_order": {"type": "integer", "description": "Display order"},
        },
        "required": ["name"],
        "additionalProperties": False,
    }

    def execute(self, args, request):
        from tables.models import Zone
        z = Zone.objects.create(
            name=args['name'],
            description=args.get('description', ''),
            color=args.get('color', ''),
            sort_order=args.get('sort_order', 0),
        )
        return {"id": str(z.id), "name": z.name, "created": True}


@register_tool
class ListTables(AssistantTool):
    name = "list_tables"
    description = "List tables with optional filters. Returns number, name, capacity, zone, status, shape."
    module_id = "tables"
    required_permission = "tables.view_table"
    parameters = {
        "type": "object",
        "properties": {
            "zone_id": {"type": "string", "description": "Filter by zone ID"},
            "status": {"type": "string", "description": "Filter by status: available, occupied, reserved, blocked"},
            "is_active": {"type": "boolean", "description": "Filter by active status"},
        },
        "required": [],
        "additionalProperties": False,
    }

    def execute(self, args, request):
        from tables.models import Table
        qs = Table.objects.select_related('zone').all()
        if args.get('zone_id'):
            qs = qs.filter(zone_id=args['zone_id'])
        if args.get('status'):
            qs = qs.filter(status=args['status'])
        if 'is_active' in args:
            qs = qs.filter(is_active=args['is_active'])
        return {
            "tables": [
                {
                    "id": str(t.id),
                    "number": t.number,
                    "name": t.name,
                    "capacity": t.capacity,
                    "shape": t.shape,
                    "status": t.status,
                    "is_active": t.is_active,
                    "zone": t.zone.name if t.zone else None,
                    "zone_id": str(t.zone_id) if t.zone_id else None,
                }
                for t in qs
            ],
            "total": qs.count(),
        }


@register_tool
class CreateTable(AssistantTool):
    name = "create_table"
    description = "Create a new table. Specify number, capacity, zone, and shape."
    module_id = "tables"
    required_permission = "tables.add_table"
    requires_confirmation = True
    parameters = {
        "type": "object",
        "properties": {
            "number": {"type": "string", "description": "Table number/identifier (e.g., '1', 'T5', 'B3')"},
            "name": {"type": "string", "description": "Friendly name (e.g., 'Mesa ventana')"},
            "capacity": {"type": "integer", "description": "Seating capacity (default 4)"},
            "zone_id": {"type": "string", "description": "Zone ID to assign to"},
            "shape": {"type": "string", "description": "Shape: square, round, rectangle (default square)"},
            "position_x": {"type": "integer", "description": "X position on floor plan"},
            "position_y": {"type": "integer", "description": "Y position on floor plan"},
        },
        "required": ["number"],
        "additionalProperties": False,
    }

    def execute(self, args, request):
        from tables.models import Table
        t = Table.objects.create(
            number=args['number'],
            name=args.get('name', ''),
            capacity=args.get('capacity', 4),
            zone_id=args.get('zone_id'),
            shape=args.get('shape', 'square'),
            position_x=args.get('position_x', 0),
            position_y=args.get('position_y', 0),
        )
        return {"id": str(t.id), "number": t.number, "capacity": t.capacity, "created": True}


@register_tool
class UpdateTable(AssistantTool):
    name = "update_table"
    description = "Update a table's properties (capacity, name, zone, status, shape)."
    module_id = "tables"
    required_permission = "tables.change_table"
    requires_confirmation = True
    parameters = {
        "type": "object",
        "properties": {
            "table_id": {"type": "string", "description": "Table ID"},
            "number": {"type": "string", "description": "New table number"},
            "name": {"type": "string", "description": "New friendly name"},
            "capacity": {"type": "integer", "description": "New capacity"},
            "zone_id": {"type": "string", "description": "New zone ID"},
            "shape": {"type": "string", "description": "New shape"},
            "status": {"type": "string", "description": "New status: available, occupied, reserved, blocked"},
            "is_active": {"type": "boolean", "description": "Active/inactive"},
        },
        "required": ["table_id"],
        "additionalProperties": False,
    }

    def execute(self, args, request):
        from tables.models import Table
        t = Table.objects.get(id=args['table_id'])
        for field in ['number', 'name', 'capacity', 'zone_id', 'shape', 'status', 'is_active']:
            if field in args:
                setattr(t, field, args[field])
        t.save()
        return {"id": str(t.id), "number": t.number, "updated": True}


@register_tool
class BulkCreateTables(AssistantTool):
    name = "bulk_create_tables"
    description = "Create multiple tables at once. Useful for initial setup (e.g., 'create 10 tables for zone Interior')."
    module_id = "tables"
    required_permission = "tables.add_table"
    requires_confirmation = True
    parameters = {
        "type": "object",
        "properties": {
            "count": {"type": "integer", "description": "Number of tables to create"},
            "start_number": {"type": "integer", "description": "Starting table number (default 1)"},
            "prefix": {"type": "string", "description": "Number prefix (e.g., 'T' for T1, T2...)"},
            "capacity": {"type": "integer", "description": "Default capacity for all tables (default 4)"},
            "zone_id": {"type": "string", "description": "Zone ID for all tables"},
            "shape": {"type": "string", "description": "Shape for all tables (default square)"},
        },
        "required": ["count"],
        "additionalProperties": False,
    }

    def execute(self, args, request):
        from tables.models import Table
        count = args['count']
        start = args.get('start_number', 1)
        prefix = args.get('prefix', '')
        capacity = args.get('capacity', 4)
        zone_id = args.get('zone_id')
        shape = args.get('shape', 'square')

        created = []
        for i in range(count):
            num = start + i
            t = Table.objects.create(
                number=f"{prefix}{num}",
                capacity=capacity,
                zone_id=zone_id,
                shape=shape,
                position_x=(i % 5) * 120,
                position_y=(i // 5) * 120,
            )
            created.append({"id": str(t.id), "number": t.number})

        return {"created": created, "total": len(created)}


@register_tool
class OpenTableSession(AssistantTool):
    name = "open_table_session"
    description = "Open a table session (seat guests at a table)."
    module_id = "tables"
    required_permission = "tables.add_tablesession"
    requires_confirmation = True
    parameters = {
        "type": "object",
        "properties": {
            "table_id": {"type": "string", "description": "Table ID"},
            "guests_count": {"type": "integer", "description": "Number of guests"},
            "waiter_id": {"type": "string", "description": "Waiter user ID"},
            "notes": {"type": "string", "description": "Session notes"},
        },
        "required": ["table_id", "guests_count"],
        "additionalProperties": False,
    }

    def execute(self, args, request):
        from tables.models import Table, TableSession
        table = Table.objects.get(id=args['table_id'])
        session = TableSession.objects.create(
            table=table,
            guests_count=args['guests_count'],
            waiter_id=args.get('waiter_id'),
            notes=args.get('notes', ''),
        )
        table.set_status('occupied')
        return {
            "session_id": str(session.id),
            "table_number": table.number,
            "guests": session.guests_count,
            "opened": True,
        }


@register_tool
class ListTableSessions(AssistantTool):
    name = "list_table_sessions"
    description = "List table sessions (active or historical)."
    module_id = "tables"
    required_permission = "tables.view_tablesession"
    parameters = {
        "type": "object",
        "properties": {
            "status": {"type": "string", "description": "Filter: active, closed, transferred"},
            "zone_id": {"type": "string", "description": "Filter by zone"},
            "limit": {"type": "integer", "description": "Max results (default 20)"},
        },
        "required": [],
        "additionalProperties": False,
    }

    def execute(self, args, request):
        from tables.models import TableSession
        qs = TableSession.objects.select_related('table', 'waiter').all()
        if args.get('status'):
            qs = qs.filter(status=args['status'])
        if args.get('zone_id'):
            qs = qs.filter(table__zone_id=args['zone_id'])
        limit = args.get('limit', 20)
        sessions = qs.order_by('-opened_at')[:limit]
        return {
            "sessions": [
                {
                    "id": str(s.id),
                    "table_number": s.table.number,
                    "guests_count": s.guests_count,
                    "status": s.status,
                    "waiter": s.waiter.display_name if s.waiter else None,
                    "opened_at": s.opened_at.isoformat() if s.opened_at else None,
                    "duration_minutes": s.duration_minutes,
                }
                for s in sessions
            ]
        }
