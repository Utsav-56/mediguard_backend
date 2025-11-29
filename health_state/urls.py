from django.urls import path
from .views import (
    # Template views
    HealthTemplateListView,
    HealthTemplateDetailView,
    HealthTemplateCategoriesView,
    # Record views
    HealthRecordListView,
    HealthRecordDetailView,
    HealthRecordByTemplateView,
    HealthRecordLatestView,
    HealthRecordStatsView,
    HealthRecordSummaryView,
)

urlpatterns = [
    # Template endpoints (read-only for users)
    path('templates/', HealthTemplateListView.as_view(), name='health-template-list'),
    path('templates/categories/', HealthTemplateCategoriesView.as_view(), name='health-template-categories'),
    path('templates/<int:pk>/', HealthTemplateDetailView.as_view(), name='health-template-detail'),
    path('templates/slug/<slug:slug>/', HealthTemplateDetailView.as_view(), name='health-template-by-slug'),
    
    # Record endpoints
    path('records/', HealthRecordListView.as_view(), name='health-record-list'),
    path('records/latest/', HealthRecordLatestView.as_view(), name='health-record-latest'),
    path('records/summary/', HealthRecordSummaryView.as_view(), name='health-record-summary'),
    path('records/template/<slug:template_slug>/', HealthRecordByTemplateView.as_view(), name='health-record-by-template'),
    path('records/stats/<slug:template_slug>/', HealthRecordStatsView.as_view(), name='health-record-stats'),
    path('records/<int:pk>/', HealthRecordDetailView.as_view(), name='health-record-detail'),
]
