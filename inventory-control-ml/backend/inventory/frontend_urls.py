from django.urls import path
from .views import (
    DashboardView, 
    DataUploadView,
    InsightsView,
    NotificationsView,
    ReportsView,BusinessView
)

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('upload/', DataUploadView.as_view(), name='upload'),
    path('insights/', InsightsView.as_view(), name='insights'),
    path('notifications/', NotificationsView.as_view(), name='notifications'),
    path('reports/', ReportsView.as_view(), name='reports'),
    # In urls.py
    path('business/', BusinessView.as_view(), name='business'),
]