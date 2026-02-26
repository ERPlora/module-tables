"""
Tables Module Views
Floor plan, zones, tables, and sessions management.
"""

import json

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db.models import Q, Count

from apps.core.htmx import htmx_view
from apps.accounts.decorators import login_required

from .models import Zone, Table, TableSession
from .forms import ZoneForm, TableForm


def _hub_id(request):
    return request.session.get('hub_id')


# =============================================================================
# Floor Plan
# =============================================================================

@login_required
@htmx_view('tables/pages/index.html', 'tables/partials/floor_plan.html')
def index(request):
    return floor_plan(request)


@login_required
@htmx_view('tables/pages/index.html', 'tables/partials/floor_plan.html')
def floor_plan(request):
    hub = _hub_id(request)
    zone_filter = request.GET.get('zone', '')

    zones = Zone.objects.filter(
        hub_id=hub, is_active=True, is_deleted=False,
    ).order_by('sort_order', 'name')

    tables_qs = Table.objects.filter(
        hub_id=hub, is_active=True, is_deleted=False,
    ).select_related('zone')

    if zone_filter:
        tables_qs = tables_qs.filter(zone_id=zone_filter)

    tables = tables_qs.order_by('zone__sort_order', 'number')

    status_counts = {
        'available': tables.filter(status='available').count(),
        'occupied': tables.filter(status='occupied').count(),
        'reserved': tables.filter(status='reserved').count(),
        'blocked': tables.filter(status='blocked').count(),
    }

    tables_json = json.dumps([{
        'id': str(t.pk),
        'number': t.number,
        'name': t.name,
        'display_name': t.display_name,
        'capacity': t.capacity,
        'position_x': t.position_x,
        'position_y': t.position_y,
        'width': t.width,
        'height': t.height,
        'shape': t.shape,
        'status': t.status,
        'zone_id': str(t.zone_id) if t.zone_id else None,
        'zone_name': t.zone.name if t.zone else None,
    } for t in tables])

    return {
        'zones': zones,
        'tables': tables,
        'tables_json': tables_json,
        'zone_filter': zone_filter,
        'status_counts': status_counts,
        'total_tables': tables.count(),
    }


# =============================================================================
# Zones
# =============================================================================

@login_required
@htmx_view('tables/pages/index.html', 'tables/partials/zones.html')
def zones(request):
    hub = _hub_id(request)
    zones_qs = Zone.objects.filter(
        hub_id=hub, is_deleted=False,
    ).annotate(
        table_count=Count('tables', filter=Q(tables__is_deleted=False)),
    ).order_by('sort_order', 'name')

    return {'zones': zones_qs}


@login_required
@htmx_view('tables/pages/index.html', 'tables/partials/zone_form.html')
def zone_add(request):
    hub = _hub_id(request)

    if request.method == 'POST':
        form = ZoneForm(request.POST)
        if form.is_valid():
            zone = form.save(commit=False)
            zone.hub_id = hub
            zone.save()
            return {
                'zones': Zone.objects.filter(hub_id=hub, is_deleted=False),
                'template': 'tables/partials/zones.html',
            }
    else:
        form = ZoneForm()

    return {'form': form, 'is_new': True}


@login_required
@htmx_view('tables/pages/index.html', 'tables/partials/zone_form.html')
def zone_edit(request, zone_id):
    hub = _hub_id(request)
    zone = get_object_or_404(Zone, pk=zone_id, hub_id=hub, is_deleted=False)

    if request.method == 'POST':
        form = ZoneForm(request.POST, instance=zone)
        if form.is_valid():
            form.save()
            return {
                'zones': Zone.objects.filter(hub_id=hub, is_deleted=False),
                'template': 'tables/partials/zones.html',
            }
    else:
        form = ZoneForm(instance=zone)

    return {'form': form, 'zone': zone, 'is_new': False}


@login_required
@require_POST
def zone_delete(request, zone_id):
    hub = _hub_id(request)
    zone = get_object_or_404(Zone, pk=zone_id, hub_id=hub, is_deleted=False)
    zone.is_deleted = True
    zone.deleted_at = timezone.now()
    zone.save(update_fields=['is_deleted', 'deleted_at', 'updated_at'])
    return JsonResponse({'success': True, 'message': str(_('Zone deleted'))})


# =============================================================================
# Tables
# =============================================================================

@login_required
@htmx_view('tables/pages/index.html', 'tables/partials/tables_list.html')
def tables_list(request):
    hub = _hub_id(request)
    search_query = request.GET.get('q', '').strip()
    zone_filter = request.GET.get('zone', '')
    status_filter = request.GET.get('status', '')

    tables_qs = Table.objects.filter(
        hub_id=hub, is_deleted=False,
    ).select_related('zone').order_by('zone__sort_order', 'number')

    if search_query:
        tables_qs = tables_qs.filter(
            Q(number__icontains=search_query) | Q(name__icontains=search_query)
        )
    if zone_filter:
        tables_qs = tables_qs.filter(zone_id=zone_filter)
    if status_filter:
        tables_qs = tables_qs.filter(status=status_filter)

    zones_qs = Zone.objects.filter(
        hub_id=hub, is_active=True, is_deleted=False,
    ).order_by('sort_order', 'name')

    return {
        'tables': tables_qs,
        'zones': zones_qs,
        'search_query': search_query,
        'zone_filter': zone_filter,
        'status_filter': status_filter,
        'status_choices': Table.STATUS_CHOICES,
    }


@login_required
@htmx_view('tables/pages/index.html', 'tables/partials/table_form.html')
def table_add(request):
    hub = _hub_id(request)
    zones_qs = Zone.objects.filter(
        hub_id=hub, is_active=True, is_deleted=False,
    ).order_by('sort_order', 'name')

    if request.method == 'POST':
        form = TableForm(request.POST)
        form.fields['zone'].queryset = zones_qs
        if form.is_valid():
            table = form.save(commit=False)
            table.hub_id = hub
            table.save()
            return {
                'tables': Table.objects.filter(hub_id=hub, is_deleted=False),
                'zones': zones_qs,
                'template': 'tables/partials/tables_list.html',
            }
    else:
        form = TableForm()
        form.fields['zone'].queryset = zones_qs

    return {'form': form, 'zones': zones_qs, 'is_new': True}


@login_required
@htmx_view('tables/pages/index.html', 'tables/partials/table_form.html')
def table_edit(request, table_id):
    hub = _hub_id(request)
    table = get_object_or_404(Table, pk=table_id, hub_id=hub, is_deleted=False)
    zones_qs = Zone.objects.filter(
        hub_id=hub, is_active=True, is_deleted=False,
    ).order_by('sort_order', 'name')

    if request.method == 'POST':
        form = TableForm(request.POST, instance=table)
        form.fields['zone'].queryset = zones_qs
        if form.is_valid():
            form.save()
            return {
                'tables': Table.objects.filter(hub_id=hub, is_deleted=False),
                'zones': zones_qs,
                'template': 'tables/partials/tables_list.html',
            }
    else:
        form = TableForm(instance=table)
        form.fields['zone'].queryset = zones_qs

    return {'form': form, 'table': table, 'zones': zones_qs, 'is_new': False}


@login_required
@require_POST
def table_delete(request, table_id):
    hub = _hub_id(request)
    table = get_object_or_404(Table, pk=table_id, hub_id=hub, is_deleted=False)
    table.is_deleted = True
    table.deleted_at = timezone.now()
    table.save(update_fields=['is_deleted', 'deleted_at', 'updated_at'])
    return JsonResponse({'success': True, 'message': str(_('Table deleted'))})


@login_required
@htmx_view('tables/pages/index.html', 'tables/partials/table_detail.html')
def table_detail(request, table_id):
    hub = _hub_id(request)
    table = get_object_or_404(Table, pk=table_id, hub_id=hub, is_deleted=False)

    current_session = table.current_session
    recent_sessions = table.sessions.filter(
        is_deleted=False,
    ).exclude(status='active').order_by('-opened_at')[:10]

    available_tables = Table.objects.filter(
        hub_id=hub, is_deleted=False, is_active=True, status='available',
    ).exclude(pk=table_id).order_by('zone__sort_order', 'number')

    return {
        'table': table,
        'current_session': current_session,
        'recent_sessions': recent_sessions,
        'available_tables': available_tables,
    }


@login_required
@require_POST
def table_update_status(request, table_id):
    hub = _hub_id(request)
    table = get_object_or_404(Table, pk=table_id, hub_id=hub, is_deleted=False)
    new_status = request.POST.get('status')
    if new_status in dict(Table.STATUS_CHOICES):
        table.set_status(new_status)
        return JsonResponse({'success': True, 'message': str(_('Status updated')), 'status': new_status})
    return JsonResponse({'success': False, 'message': str(_('Invalid status'))}, status=400)


@login_required
@require_POST
def table_update_position(request, table_id):
    hub = _hub_id(request)
    table = get_object_or_404(Table, pk=table_id, hub_id=hub, is_deleted=False)
    try:
        position_x = max(0, min(100, int(request.POST.get('position_x', table.position_x))))
        position_y = max(0, min(100, int(request.POST.get('position_y', table.position_y))))
        table.position_x = position_x
        table.position_y = position_y
        table.save(update_fields=['position_x', 'position_y', 'updated_at'])
        return JsonResponse({'success': True, 'position_x': position_x, 'position_y': position_y})
    except (ValueError, TypeError):
        return JsonResponse({'success': False, 'message': str(_('Invalid position'))}, status=400)


# =============================================================================
# Sessions
# =============================================================================

@login_required
@htmx_view('tables/pages/index.html', 'tables/partials/sessions.html')
def sessions(request):
    hub = _hub_id(request)
    show_closed = request.GET.get('show_closed', '') == 'true'

    sessions_qs = TableSession.objects.filter(
        hub_id=hub, is_deleted=False,
    ).select_related('table', 'table__zone', 'waiter')

    if not show_closed:
        sessions_qs = sessions_qs.filter(status='active')

    sessions_qs = sessions_qs.order_by('-opened_at')[:100]

    return {'sessions': sessions_qs, 'show_closed': show_closed}


@login_required
@require_POST
def session_open(request, table_id):
    hub = _hub_id(request)
    table = get_object_or_404(Table, pk=table_id, hub_id=hub, is_deleted=False)

    if table.status != 'available':
        return JsonResponse({'success': False, 'message': str(_('Table is not available'))}, status=400)

    from apps.accounts.models import LocalUser
    user_id = request.session.get('local_user_id')
    waiter = LocalUser.objects.filter(id=user_id).first() if user_id else None

    guests_count = int(request.POST.get('guests_count', 1))
    notes = request.POST.get('notes', '')

    session = TableSession.objects.create(
        hub_id=hub,
        table=table,
        guests_count=guests_count,
        waiter=waiter,
        notes=notes,
    )
    table.set_status('occupied')

    return JsonResponse({
        'success': True,
        'message': str(_('Table opened')),
        'session_id': str(session.pk),
    })


@login_required
@require_POST
def session_close(request, session_id):
    hub = _hub_id(request)
    session = get_object_or_404(
        TableSession, pk=session_id, hub_id=hub, is_deleted=False, status='active',
    )
    session.close()
    return JsonResponse({'success': True, 'message': str(_('Table closed'))})


@login_required
@require_POST
def session_transfer(request, session_id):
    hub = _hub_id(request)
    session = get_object_or_404(
        TableSession, pk=session_id, hub_id=hub, is_deleted=False, status='active',
    )
    target_table_id = request.POST.get('target_table_id')
    target_table = get_object_or_404(
        Table, pk=target_table_id, hub_id=hub, is_deleted=False, is_active=True, status='available',
    )

    from apps.accounts.models import LocalUser
    user_id = request.session.get('local_user_id')
    waiter = LocalUser.objects.filter(id=user_id).first() if user_id else None

    new_session = session.transfer_to(target_table, waiter=waiter)
    return JsonResponse({
        'success': True,
        'message': str(_('Session transferred')),
        'new_session_id': str(new_session.pk),
    })


# =============================================================================
# Settings
# =============================================================================

@login_required
@htmx_view('tables/pages/index.html', 'tables/partials/settings.html')
def settings(request):
    hub = _hub_id(request)

    zones_qs = Zone.objects.filter(hub_id=hub, is_deleted=False).annotate(
        table_count=Count('tables', filter=Q(tables__is_deleted=False)),
    ).order_by('sort_order', 'name')

    total_tables = Table.objects.filter(hub_id=hub, is_deleted=False).count()
    active_tables = Table.objects.filter(hub_id=hub, is_deleted=False, is_active=True).count()
    active_sessions = TableSession.objects.filter(hub_id=hub, is_deleted=False, status='active').count()

    return {
        'zones': zones_qs,
        'total_tables': total_tables,
        'active_tables': active_tables,
        'active_sessions': active_sessions,
    }
