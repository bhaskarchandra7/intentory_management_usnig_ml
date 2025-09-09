from django.urls import path
from .views import (
    DashboardView,
    DataUploadView,
    InsightsView,
    NotificationsView,
    ReportsView,
    CustomLoginView,
    TrainModelView,
    PredictView
)

urlpatterns = [
    # Core URLs
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('upload/', DataUploadView.as_view(), name='upload'),
    path('insights/', InsightsView.as_view(), name='insights'),
    path('notifications/', NotificationsView.as_view(), name='notifications'),
    path('reports/', ReportsView.as_view(), name='reports'),
    
    # ML URLs
    path('api/train/<int:dataset_id>/', TrainModelView.as_view(), name='train_model'),
    path('api/predict/<int:model_id>/', PredictView.as_view(), name='predict'),
]
