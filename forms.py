from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Zone, Table, TableSession


class ZoneForm(forms.ModelForm):
    class Meta:
        model = Zone
        fields = ['name', 'description', 'color', 'sort_order', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'input', 'placeholder': _('Zone name'),
            }),
            'description': forms.Textarea(attrs={
                'class': 'textarea', 'rows': 3,
                'placeholder': _('Optional description'),
            }),
            'color': forms.Select(attrs={'class': 'select'}, choices=[
                ('primary', _('Primary')),
                ('secondary', _('Secondary')),
                ('success', _('Success')),
                ('warning', _('Warning')),
                ('danger', _('Danger')),
                ('info', _('Info')),
            ]),
            'sort_order': forms.NumberInput(attrs={
                'class': 'input', 'min': '0',
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'toggle'}),
        }


class TableForm(forms.ModelForm):
    class Meta:
        model = Table
        fields = [
            'zone', 'number', 'name', 'capacity',
            'position_x', 'position_y', 'width', 'height',
            'shape', 'status', 'is_active',
        ]
        widgets = {
            'zone': forms.Select(attrs={'class': 'select'}),
            'number': forms.TextInput(attrs={
                'class': 'input', 'placeholder': _('e.g. 1, A1'),
            }),
            'name': forms.TextInput(attrs={
                'class': 'input', 'placeholder': _('Optional friendly name'),
            }),
            'capacity': forms.NumberInput(attrs={
                'class': 'input', 'min': '1',
            }),
            'position_x': forms.NumberInput(attrs={
                'class': 'input', 'min': '0', 'max': '100',
            }),
            'position_y': forms.NumberInput(attrs={
                'class': 'input', 'min': '0', 'max': '100',
            }),
            'width': forms.NumberInput(attrs={
                'class': 'input', 'min': '5', 'max': '50',
            }),
            'height': forms.NumberInput(attrs={
                'class': 'input', 'min': '5', 'max': '50',
            }),
            'shape': forms.Select(attrs={'class': 'select'}),
            'status': forms.Select(attrs={'class': 'select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'toggle'}),
        }


class TableSessionForm(forms.ModelForm):
    class Meta:
        model = TableSession
        fields = ['table', 'guests_count', 'waiter', 'notes']
        widgets = {
            'table': forms.Select(attrs={'class': 'select'}),
            'guests_count': forms.NumberInput(attrs={
                'class': 'input', 'min': '1',
            }),
            'waiter': forms.Select(attrs={'class': 'select'}),
            'notes': forms.Textarea(attrs={
                'class': 'textarea', 'rows': 2,
            }),
        }


class OpenTableForm(forms.Form):
    guests_count = forms.IntegerField(
        min_value=1, initial=1,
        widget=forms.NumberInput(attrs={'class': 'input', 'min': '1'}),
        label=_('Number of Guests'),
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'textarea', 'rows': 2,
            'placeholder': _('Optional notes'),
        }),
        label=_('Notes'),
    )


class TransferTableForm(forms.Form):
    target_table = forms.ModelChoiceField(
        queryset=Table.objects.none(),
        widget=forms.Select(attrs={'class': 'select'}),
        label=_('Transfer to Table'),
    )

    def __init__(self, *args, hub_id=None, exclude_table=None, **kwargs):
        super().__init__(*args, **kwargs)
        if hub_id:
            qs = Table.objects.filter(
                hub_id=hub_id, is_deleted=False, is_active=True, status='available',
            )
            if exclude_table:
                qs = qs.exclude(pk=exclude_table.pk)
            self.fields['target_table'].queryset = qs
