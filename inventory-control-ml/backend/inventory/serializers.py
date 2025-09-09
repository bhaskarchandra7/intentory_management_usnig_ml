from rest_framework import serializers
from .models import Business, Dataset, MLModel, Notification, Report, Prediction

class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = ['id', 'name', 'industry', 'created_at']

class DatasetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dataset
        fields = ['id', 'business', 'name', 'file', 'uploaded_at', 'columns', 'row_count']

class MLModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = MLModel
        fields = ['id', 'dataset', 'name', 'model_type', 'algorithm', 'accuracy', 'created_at']

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'business', 'message', 'notification_type', 'is_read', 'created_at']

class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['id', 'business', 'title', 'content', 'generated_at', 'report_file']

class PredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prediction
        fields = ['id', 'ml_model', 'input_data', 'output_data', 'created_at']