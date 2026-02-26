# Tables Module

> **Note**: This module is currently disabled.

Restaurant floor plan and table management with zones, table tracking, and customer sessions.

## Features

- Visual floor plan with table positioning (X/Y coordinates, width, height)
- Zone management for organizing areas (e.g., Main Hall, Terrace, VIP) with color coding and sort order
- Table management with number, name, capacity, and shape (square, round, rectangle)
- Real-time table status tracking: available, occupied, reserved, blocked
- Customer session management with open/close lifecycle
- Session transfer between tables with history tracking
- Waiter assignment per session
- Guest count and duration tracking per session
- Table activation/deactivation

## Installation

This module is installed automatically via the ERPlora Marketplace.

## Configuration

Access settings via: **Menu > Tables > Settings**

## Usage

Access via: **Menu > Tables**

### Views

| View | URL | Description |
|------|-----|-------------|
| Floor Plan | `/m/tables/floor_plan/` | Visual floor plan with table layout and status |
| Zones | `/m/tables/zones/` | Manage floor zones (areas) |
| Tables | `/m/tables/tables/` | Manage individual tables and their properties |
| Sessions | `/m/tables/sessions/` | View and manage active and past table sessions |
| Settings | `/m/tables/settings/` | Configure tables module settings |

## Models

| Model | Description |
|-------|-------------|
| `Zone` | Named area within the venue (e.g., Main Hall, Terrace) with color, active status, and sort order |
| `Table` | Physical table with number, name, capacity, shape, floor plan position, status (available/occupied/reserved/blocked), and zone assignment |
| `TableSession` | Customer session at a table tracking opened/closed times, guest count, assigned waiter, status (active/closed/transferred), and transfer history |

## Permissions

| Permission | Description |
|------------|-------------|
| `tables.view_zone` | View zones |
| `tables.add_zone` | Create new zones |
| `tables.change_zone` | Edit existing zones |
| `tables.delete_zone` | Delete zones |
| `tables.view_table` | View tables |
| `tables.add_table` | Create new tables |
| `tables.change_table` | Edit existing tables |
| `tables.delete_table` | Delete tables |
| `tables.view_tablesession` | View table sessions |
| `tables.add_tablesession` | Create new table sessions |
| `tables.change_tablesession` | Edit existing table sessions |
| `tables.delete_tablesession` | Delete table sessions |

## License

MIT

## Author

ERPlora Team - support@erplora.com
