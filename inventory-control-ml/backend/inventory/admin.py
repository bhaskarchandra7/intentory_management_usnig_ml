# inventory/admin.py
from django.contrib import admin
from .models import Business, Dataset, MLModel, Notification, Report, Prediction

admin.site.register(Business)
admin.site.register(Dataset)
admin.site.register(MLModel)
admin.site.register(Notification)
admin.site.register(Report)
admin.site.register(Prediction)