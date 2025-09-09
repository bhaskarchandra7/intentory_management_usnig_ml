from ..models import Notification, MLModel, Dataset, Business
from datetime import datetime
import pandas as pd

class ReportGenerator:
    def __init__(self, business):
        self.business = business
    
    def generate(self):
        """Generate a comprehensive business report"""
        report_lines = []
        
        # Header
        report_lines.append(f"BUSINESS REPORT - {self.business.name.upper()}")
        report_lines.append(f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        report_lines.append("="*50 + "\n")
        
        # Business Information
        report_lines.append("BUSINESS INFORMATION:")
        report_lines.append(f"Industry: {self.business.industry}")
        report_lines.append(f"Member since: {self.business.created_at.date()}")
        report_lines.append("\n")
        
        # Dataset Analysis
        latest_dataset = Dataset.objects.filter(business=self.business).order_by('-uploaded_at').first()
        if latest_dataset:
            report_lines.append("DATASET ANALYSIS:")
            report_lines.append(f"Latest dataset: {latest_dataset.name}")
            report_lines.append(f"Uploaded on: {latest_dataset.uploaded_at.date()}")
            report_lines.append(f"Dimensions: {latest_dataset.row_count} rows, {len(latest_dataset.columns)} columns")
            
            try:
                # Load data for analysis
                df = pd.read_csv(latest_dataset.file.path)
                
                # Inventory analysis
                if all(col in df.columns for col in ['current_stock', 'min_required']):
                    low_stock = df[df['current_stock'] < df['min_required']]
                    report_lines.append(f"\nINVENTORY STATUS:")
                    report_lines.append(f"Total products: {len(df)}")
                    report_lines.append(f"Products needing restock: {len(low_stock)}")
                
                # Sales analysis
                if 'sales_quantity' in df.columns:
                    total_sales = df['sales_quantity'].sum()
                    report_lines.append(f"\nSALES ANALYSIS:")
                    report_lines.append(f"Total sales: {total_sales}")
            except Exception as e:
                report_lines.append(f"\nError analyzing dataset: {str(e)}")
        
        # Notifications Summary
        notifications = Notification.objects.filter(business=self.business).order_by('-created_at')[:10]
        if notifications.exists():
            report_lines.append("\nRECENT NOTIFICATIONS:")
            for note in notifications:
                report_lines.append(f"- [{note.created_at.date()}] {note.notification_type.upper()}: {note.message}")
        
        # Recommendations
        report_lines.append("\nRECOMMENDATIONS:")
        if Notification.objects.filter(business=self.business, notification_type='stock_alert', is_read=False).exists():
            report_lines.append("- Restock items with low inventory immediately")
        
        if latest_dataset and not MLModel.objects.filter(dataset=latest_dataset).exists():
            report_lines.append("- Train a machine learning model on your latest dataset")
        
        return "\n".join(report_lines)