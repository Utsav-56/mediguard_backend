from django.urls import path
from .views import (
    IntakeListView,
    IntakeDetailView,
    IntakeTodayView,
    IntakeByMedicineView,
    IntakeMarkTakenView,
    IntakeMarkSkippedView,
    IntakeGenerateView,
    IntakeStatsView,
)

urlpatterns = [
    # List and create intakes
    path('list/', IntakeListView.as_view(), name='intake-list'),
    
    # Get today's intakes
    path('today/', IntakeTodayView.as_view(), name='intake-today'),
    
    # Get intakes by medicine
    path('medicine/<int:medicine_id>/', IntakeByMedicineView.as_view(), name='intake-by-medicine'),
    
    # Quick actions
    path('mark-taken/<int:pk>/', IntakeMarkTakenView.as_view(), name='intake-mark-taken'),
    path('mark-skipped/<int:pk>/', IntakeMarkSkippedView.as_view(), name='intake-mark-skipped'),
    
    # Bulk generate intakes
    path('generate/', IntakeGenerateView.as_view(), name='intake-generate'),
    
    # Statistics
    path('stats/', IntakeStatsView.as_view(), name='intake-stats'),
    
    # Detail view (get, update, delete)
    path('<int:pk>/', IntakeDetailView.as_view(), name='intake-detail'),
]
