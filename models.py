"""
Tables Module Models
Zones, tables, and sessions for restaurant floor plan management.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.validators import MinValueValidator

from apps.core.models import HubBaseModel


class Zone(HubBaseModel):
    """Zone represents an area (e.g., Main Hall, Terrace, VIP)."""

    name = models.CharField(_('Name'), max_length=100)
    description = models.TextField(_('Description'), blank=True, default='')
    color = models.CharField(
        _('Color'), max_length=20, blank=True, default='primary',
        help_text=_('Color for visual identification'),
    )
    is_active = models.BooleanField(_('Active'), default=True)
    sort_order = models.PositiveIntegerField(_('Sort Order'), default=0)

    class Meta(HubBaseModel.Meta):
        db_table = 'tables_zone'
        verbose_name = _('Zone')
        verbose_name_plural = _('Zones')
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name

    @property
    def table_count(self):
        return self.tables.filter(is_deleted=False).count()

    @property
    def available_tables(self):
        return self.tables.filter(
            is_deleted=False, is_active=True, status='available',
        ).count()


class Table(HubBaseModel):
    """Physical table in the restaurant."""

    SHAPE_CHOICES = [
        ('square', _('Square')),
        ('round', _('Round')),
        ('rectangle', _('Rectangle')),
    ]

    STATUS_CHOICES = [
        ('available', _('Available')),
        ('occupied', _('Occupied')),
        ('reserved', _('Reserved')),
        ('blocked', _('Blocked')),
    ]

    zone = models.ForeignKey(
        Zone, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='tables',
        verbose_name=_('Zone'),
    )
    number = models.CharField(_('Table Number'), max_length=20)
    name = models.CharField(
        _('Name'), max_length=100, blank=True, default='',
        help_text=_('Optional friendly name (e.g., "Window Table")'),
    )
    capacity = models.PositiveIntegerField(
        _('Capacity'), default=4,
        validators=[MinValueValidator(1)],
        help_text=_('Maximum number of guests'),
    )

    # Floor plan position
    position_x = models.PositiveIntegerField(_('Position X'), default=0)
    position_y = models.PositiveIntegerField(_('Position Y'), default=0)
    width = models.PositiveIntegerField(_('Width'), default=10)
    height = models.PositiveIntegerField(_('Height'), default=10)
    shape = models.CharField(
        _('Shape'), max_length=20,
        choices=SHAPE_CHOICES, default='square',
    )

    status = models.CharField(
        _('Status'), max_length=20,
        choices=STATUS_CHOICES, default='available', db_index=True,
    )
    is_active = models.BooleanField(_('Active'), default=True)

    class Meta(HubBaseModel.Meta):
        db_table = 'tables_table'
        verbose_name = _('Table')
        verbose_name_plural = _('Tables')
        ordering = ['zone__sort_order', 'number']
        indexes = [
            models.Index(fields=['hub_id', 'status']),
            models.Index(fields=['hub_id', 'is_active']),
        ]

    def __str__(self):
        if self.name:
            return f'{self.number} - {self.name}'
        return f'Table {self.number}'

    @property
    def display_name(self):
        if self.name:
            return f'{self.number} - {self.name}'
        return f'Table {self.number}'

    @property
    def current_session(self):
        return self.sessions.filter(is_deleted=False, status='active').first()

    def set_status(self, status):
        if status in dict(self.STATUS_CHOICES):
            self.status = status
            self.save(update_fields=['status', 'updated_at'])


class TableSession(HubBaseModel):
    """Customer session at a table."""

    STATUS_CHOICES = [
        ('active', _('Active')),
        ('closed', _('Closed')),
        ('transferred', _('Transferred')),
    ]

    table = models.ForeignKey(
        Table, on_delete=models.CASCADE,
        related_name='sessions', verbose_name=_('Table'),
    )
    opened_at = models.DateTimeField(_('Opened At'), default=timezone.now)
    closed_at = models.DateTimeField(_('Closed At'), null=True, blank=True)
    guests_count = models.PositiveIntegerField(
        _('Number of Guests'), default=1,
        validators=[MinValueValidator(1)],
    )
    waiter = models.ForeignKey(
        'accounts.LocalUser', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='table_sessions',
        verbose_name=_('Waiter'),
    )
    status = models.CharField(
        _('Status'), max_length=20,
        choices=STATUS_CHOICES, default='active', db_index=True,
    )
    notes = models.TextField(_('Notes'), blank=True, default='')
    transferred_from = models.ForeignKey(
        'self', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='transferred_to',
        verbose_name=_('Transferred From'),
    )

    class Meta(HubBaseModel.Meta):
        db_table = 'tables_session'
        verbose_name = _('Table Session')
        verbose_name_plural = _('Table Sessions')
        ordering = ['-opened_at']
        indexes = [
            models.Index(fields=['hub_id', 'status']),
            models.Index(fields=['hub_id', 'opened_at']),
        ]

    def __str__(self):
        return f'Session at {self.table} ({self.opened_at.strftime("%Y-%m-%d %H:%M")})'

    @property
    def duration(self):
        end_time = self.closed_at or timezone.now()
        return end_time - self.opened_at

    @property
    def duration_minutes(self):
        return int(self.duration.total_seconds() / 60)

    def close(self):
        self.status = 'closed'
        self.closed_at = timezone.now()
        self.save(update_fields=['status', 'closed_at', 'updated_at'])
        self.table.set_status('available')

    def transfer_to(self, new_table, waiter=None):
        self.status = 'transferred'
        self.closed_at = timezone.now()
        self.save(update_fields=['status', 'closed_at', 'updated_at'])
        self.table.set_status('available')

        new_session = TableSession.objects.create(
            hub_id=self.hub_id,
            table=new_table,
            guests_count=self.guests_count,
            waiter=waiter or self.waiter,
            notes=self.notes,
            transferred_from=self,
        )
        new_table.set_status('occupied')
        return new_session
