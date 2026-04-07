"""
HumanOS UI URL routes.

/ui/           — Dashboard
/ui/brain/     — Brain chat
/ui/financial/ — Financial overview
/ui/meetings/  — Meeting hub
/ui/memory/    — Knowledge search
/ui/settings/  — DNA config

/ui/api/...    — HTMX fragment endpoints
"""

from django.urls import path
from . import views

app_name = "ui"

urlpatterns = [
    # Pages
    path("", views.dashboard, name="dashboard"),
    path("brain/", views.brain_page, name="brain"),
    path("financial/", views.financial_page, name="financial"),
    path("meetings/", views.meetings_page, name="meetings"),
    path("memory/", views.memory_page, name="memory"),
    path("settings/", views.settings_page, name="settings"),

    # HTMX API fragments
    path("api/status-badge/", views.api_status_badge, name="api-status-badge"),
    path("api/stats-cards/", views.api_stats_cards, name="api-stats-cards"),
    path("api/body-map/", views.api_body_map, name="api-body-map"),
    path("api/health-refresh/", views.api_health_refresh, name="api-health-refresh"),
    path("api/organ-grid/", views.api_organ_grid, name="api-organ-grid"),
    path("api/organ-detail/<str:organ_name>/", views.api_organ_detail, name="api-organ-detail"),
    path("api/organ-health/<str:organ_name>/", views.api_organ_health, name="api-organ-health"),

    # Brain
    path("api/brain/chat/", views.api_brain_chat, name="api-brain-chat"),

    # Financial
    path("api/financial/summary/", views.api_financial_summary, name="api-fin-summary"),
    path("api/financial/transaction/", views.api_financial_transaction, name="api-fin-transaction"),
    path("api/financial/transactions/", views.api_financial_transactions, name="api-fin-transactions"),
    path("api/financial/recurring/", views.api_financial_recurring, name="api-fin-recurring"),

    # Meetings
    path("api/meetings/ingest/", views.api_meetings_ingest, name="api-meetings-ingest"),
    path("api/meetings/history/", views.api_meetings_history, name="api-meetings-history"),

    # Memory
    path("api/memory/search/", views.api_memory_search, name="api-memory-search"),
    path("api/memory/stats/", views.api_memory_stats, name="api-memory-stats"),

    # Settings
    path("api/settings/identity/", views.api_settings_identity, name="api-settings-identity"),
    path("api/settings/keys-status/", views.api_settings_keys_status, name="api-settings-keys"),
    path("api/settings/system-info/", views.api_settings_system_info, name="api-settings-system"),
    path("api/settings/export-dna/", views.api_settings_export_dna, name="api-settings-export"),
]
