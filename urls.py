from django.urls import path
from . import views

app_name = 'tables'

urlpatterns = [
    # Floor plan
    path('', views.index, name='index'),
    path('floor-plan/', views.floor_plan, name='floor_plan'),

    # Zones
    path('zones/', views.zones, name='zones'),
    path('zones/add/', views.zone_add, name='zone_add'),
    path('zones/<uuid:zone_id>/edit/', views.zone_edit, name='zone_edit'),
    path('zones/<uuid:zone_id>/delete/', views.zone_delete, name='zone_delete'),

    # Tables
    path('tables/', views.tables_list, name='tables_list'),
    path('tables/add/', views.table_add, name='table_add'),
    path('tables/<uuid:table_id>/', views.table_detail, name='table_detail'),
    path('tables/<uuid:table_id>/edit/', views.table_edit, name='table_edit'),
    path('tables/<uuid:table_id>/delete/', views.table_delete, name='table_delete'),
    path('tables/<uuid:table_id>/status/', views.table_update_status, name='table_update_status'),
    path('tables/<uuid:table_id>/position/', views.table_update_position, name='table_update_position'),

    # Sessions
    path('sessions/', views.sessions, name='sessions'),
    path('tables/<uuid:table_id>/open/', views.session_open, name='session_open'),
    path('sessions/<uuid:session_id>/close/', views.session_close, name='session_close'),
    path('sessions/<uuid:session_id>/transfer/', views.session_transfer, name='session_transfer'),

    # Settings
    path('settings/', views.settings, name='settings'),
]
