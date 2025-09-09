from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import Business, Dataset, MLModel, Notification, Report, Prediction
from .ml_engine.data_processor import DataProcessor
from .ml_engine.automl import AutoMLEngine
from .ml_engine.notifications import NotificationEngine
from .ml_engine.report_generator import ReportGenerator
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
import pandas as pd
import json
from datetime import datetime, timedelta  
import logging  

@method_decorator(login_required, name='dispatch')
class DashboardView(View):
    def get(self, request):
        try:
            business = Business.objects.filter(user=request.user).first()
            
            if not business:
                messages.info(request, "Please create a business profile to continue")
                return redirect('upload')
            
            datasets_count = Dataset.objects.filter(business=business).count()
            models_count = MLModel.objects.filter(dataset__business=business).count()
            reports_count = Report.objects.filter(business=business).count()
            recent_notifications = Notification.objects.filter(business=business, is_read=False).order_by('-created_at')[:5]
            
            latest_dataset = Dataset.objects.filter(business=business).order_by('-uploaded_at').first()
            
            return render(request, 'dashboard.html', {
                'business': business,
                'datasets_count': datasets_count,
                'models_count': models_count,
                'reports_count': reports_count,
                'notifications': recent_notifications,
                'latest_dataset': latest_dataset
            })
            
        except Exception as e:
            messages.error(request, f"Error loading dashboard: {str(e)}")
            return render(request, 'dashboard.html')

@method_decorator(login_required, name='dispatch')
class DataUploadView(View):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request):
        return render(request, 'data_upload.html')
    
    def post(self, request):
        try:
            if 'dataset' not in request.FILES:
                messages.error(request, "No file selected")
                return redirect('upload')
            
            file = request.FILES['dataset']
            
            if not file.name.endswith('.csv'):
                messages.error(request, "Only CSV files are supported")
                return redirect('upload')
            
            businesses = Business.objects.filter(user=request.user)
            
            if not businesses.exists():
                business = Business.objects.create(
                    user=request.user,
                    name=f"{request.user.username}'s Business",
                    industry='General'
                )
            else:
                business = businesses.latest('created_at')

            dataset = Dataset.objects.create(
                business=business,
                name=file.name,
                file=file
            )
            
            processor = DataProcessor(dataset.file.path)
            df = processor.load_data(only_preview=True)
            
            dataset.columns = list(df.columns)
            dataset.row_count = len(df)
            dataset.save()
            
            notification_engine = NotificationEngine(business)
            notification_engine.generate_initial_notifications(df)
            
            messages.success(request, f"File '{file.name}' uploaded successfully!")
            return redirect('insights')
            
        except Exception as e:
            messages.error(request, f"Error uploading file: {str(e)}")
            return redirect('upload')

logger = logging.getLogger(__name__)
@method_decorator(login_required, name='dispatch')
class InsightsView(View):
    def get(self, request):
        try:
            business = Business.objects.get(user=request.user)
            latest_dataset = Dataset.objects.filter(business=business).order_by('-uploaded_at').first()

            if not latest_dataset:
                messages.info(request, "Upload a dataset to view insights")
                return redirect('upload')

            context = {'dataset': latest_dataset}

            processor = DataProcessor(latest_dataset.file.path)
            df = processor.load_data(only_preview=True)
            df.columns = [col.lower() for col in df.columns]  

            if all(col in df.columns for col in ['date', 'sales_quantity']):
                try:
                    df['date'] = pd.to_datetime(df['date'], errors='coerce')
                    df = df.dropna(subset=['date', 'sales_quantity'])
                    df['sales_quantity'] = pd.to_numeric(df['sales_quantity'], errors='coerce').fillna(0)

                    cutoff_date = datetime.now() - timedelta(days=90)
                    recent_sales = df.copy()

                    if not recent_sales.empty:
                        daily_sales = recent_sales.groupby('date')['sales_quantity'].sum().reset_index()

                        context['sales_trend'] = json.dumps({
                            'labels': daily_sales['date'].dt.strftime('%Y-%m-%d').tolist(),
                            'data': daily_sales['sales_quantity'].tolist(),
                            'total_sales': int(daily_sales['sales_quantity'].sum()),
                            'avg_daily': round(daily_sales['sales_quantity'].mean(), 1)
                        })
                    else:
                        context['sales_warning'] = "No sales data in the last 90 days"
                except Exception as e:
                    logger.error(f"Sales data processing error: {e}")
                    context['sales_warning'] = "Error processing sales data"
            else:
                context['sales_warning'] = "Dataset missing 'date' or 'sales_quantity' columns"

            inventory_columns = ['product_name', 'current_stock', 'min_required']  
            if all(col in df.columns for col in inventory_columns):
                try:
                    inventory_data = df[inventory_columns].copy()
                    inventory_data = inventory_data.dropna()
                    
                    inventory_data['current_stock'] = pd.to_numeric(inventory_data['current_stock'], errors='coerce')
                    inventory_data['min_required'] = pd.to_numeric(inventory_data['min_required'], errors='coerce')
                    inventory_data = inventory_data.dropna()
                    
                    inventory_data['status'] = inventory_data.apply(
                        lambda x: 'Low' if x['current_stock'] < x['min_required'] else 'OK', axis=1
                    )
                    
                    context['inventory'] = inventory_data.to_dict('records')
                except Exception as e:
                    logger.error(f"Inventory data processing error: {e}")
            else:
                logger.info("Dataset missing required inventory columns")

            return render(request, 'insights.html', context)

        except Exception as e:
            logger.error(f"Insights view error: {str(e)}")
            messages.error(request, f"Error loading insights: {str(e)}")
            return redirect('dashboard')
        
@method_decorator(login_required, name='dispatch')
class NotificationsView(View):
    def get(self, request):
        try:
            business = Business.objects.get(user=request.user)
            notifications = Notification.objects.filter(business=business).order_by('-created_at')
            
            Notification.objects.filter(business=business, is_read=False).update(is_read=True)
            
            return render(request, 'notifications.html', {
                'notifications': notifications
            })
            
        except Business.DoesNotExist:
            messages.error(request, "Please create a business first")
            return redirect('dashboard')
        except Exception as e:
            messages.error(request, f"Error loading notifications: {str(e)}")
            return redirect('dashboard')

@method_decorator(login_required, name='dispatch')
class ReportsView(View):
    def get(self, request):
        try:
            business = Business.objects.get(user=request.user)
            reports = Report.objects.filter(business=business).order_by('-generated_at')
            
            return render(request, 'reports.html', {
                'reports': reports,
                'business': business
            })
            
        except Business.DoesNotExist:
            messages.error(request, "Please create a business first")
            return redirect('dashboard')
        except Exception as e:
            messages.error(request, f"Error loading reports: {str(e)}")
            return redirect('dashboard')
    
    def post(self, request):
        try:
            business = Business.objects.get(user=request.user)
            latest_dataset = Dataset.objects.filter(business=business).order_by('-uploaded_at').first()
            
            if not latest_dataset:
                messages.error(request, "No dataset available to generate report")
                return redirect('reports')
            
            generator = ReportGenerator(business)
            report_content = generator.generate()
            
            report = Report.objects.create(
                business=business,
                title=f"Business Report - {datetime.now().strftime('%Y-%m-%d')}",
                content=report_content
            )
            
            Notification.objects.create(
                business=business,
                message=f"New report generated: {report.title}",
                notification_type='report'
            )
            
            messages.success(request, "New report generated successfully")
            return redirect('reports')
            
        except Exception as e:
            messages.error(request, f"Error generating report: {str(e)}")
            return redirect('reports')

@method_decorator(login_required, name='dispatch')
class TrainModelView(View):
    def post(self, request, dataset_id):
        try:
            dataset = Dataset.objects.get(id=dataset_id, business__user=request.user)
            
            if MLModel.objects.filter(dataset=dataset).exists():
                messages.info(request, "Model already exists for this dataset")
                return redirect('insights')
            
            automl = AutoMLEngine(dataset.file.path)
            results = automl.train()
            
            model = MLModel.objects.create(
                dataset=dataset,
                name=f"Model for {dataset.name}",
                model_type=results['best_model_type'],
                algorithm=results['best_algorithm'],
                accuracy=results['best_accuracy'],
                model_file=results['model_file']
            )
            
            Notification.objects.create(
                business=dataset.business,
                message=f"New model trained: {model.name} (Accuracy: {results['best_accuracy']:.2f})",
                notification_type='model'
            )
            
            messages.success(request, f"Model trained successfully with accuracy: {results['best_accuracy']:.2f}")
            return redirect('insights')
            
        except Exception as e:
            messages.error(request, f"Error training model: {str(e)}")
            return redirect('insights')

@method_decorator(login_required, name='dispatch')
class PredictView(View):
    def post(self, request, model_id):
        try:
            model = MLModel.objects.get(id=model_id, dataset__business__user=request.user)
            input_data = request.POST.dict()
            
            automl = AutoMLEngine(model.dataset.file.path)
            prediction = automl.predict(model.model_file.path, input_data)
            
            Prediction.objects.create(
                ml_model=model,
                input_data=input_data,
                output_data={'prediction': prediction}
            )
            
            return JsonResponse({
                'status': 'success',
                'prediction': prediction
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
            
class BusinessView(View):
    @method_decorator(login_required)
    def get(self, request):
        businesses = Business.objects.filter(user=request.user)
        return render(request, 'business.html', {'businesses': businesses})
    
    def post(self, request):
        pass
    
class CustomLoginView(LoginView):
    template_name = 'login.html'
    redirect_authenticated_user = True  
    success_url = reverse_lazy('dashboard')  
    
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard.html')
        return super().get(request, *args, **kwargs)