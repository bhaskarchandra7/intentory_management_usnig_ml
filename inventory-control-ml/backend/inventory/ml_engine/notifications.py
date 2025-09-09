from django.utils import timezone
from ..models import Notification
import pandas as pd

class NotificationEngine:
    def __init__(self, business):
        self.business = business
    
    def generate_initial_notifications(self, df):
        """Generate initial notifications after data upload"""
        try:
            self._generate_upload_notification()
            self._generate_stock_alerts(df)
            self._generate_sales_trends(df)
            self._generate_seasonal_products(df)
        except Exception as e:
            print(f"Error generating notifications: {str(e)}")
    
    def _generate_upload_notification(self):
        """Notification for successful upload"""
        Notification.objects.create(
            business=self.business,
            message=f"New dataset uploaded successfully",
            notification_type='system'
        )
    
    def _generate_stock_alerts(self, df):
        """Generate notifications for low stock items"""
        if all(col in df.columns for col in ['current_stock', 'min_required']):
            low_stock = df[df['current_stock'] < df['min_required']]
            for _, item in low_stock.iterrows():
                product_name = item.get('product_name', 'Unknown product')
                Notification.objects.create(
                    business=self.business,
                    message=f"Low stock alert: {product_name} "
                            f"(Current: {item['current_stock']}, Required: {item['min_required']})",
                    notification_type='stock_alert'
                )
    
    def _generate_sales_trends(self, df):
        """Generate notifications for sales trends"""
        if all(col in df.columns for col in ['date', 'sales_quantity']):
            try:
                df['date'] = pd.to_datetime(df['date'])
                weekly_sales = df.set_index('date')['sales_quantity'].resample('W').sum()
                if len(weekly_sales) > 1:
                    trend = "increasing" if weekly_sales.iloc[-1] > weekly_sales.iloc[-2] else "decreasing"
                    Notification.objects.create(
                        business=self.business,
                        message=f"Weekly sales trend is {trend}. "
                                f"Last week: {weekly_sales.iloc[-1]}, Previous week: {weekly_sales.iloc[-2]}",
                        notification_type='sales_trend'
                    )
            except Exception as e:
                print(f"Error generating sales trends: {str(e)}")
    
    def _generate_seasonal_products(self, df):
        """Generate notifications for seasonal products"""
        if all(col in df.columns for col in ['date', 'product_name', 'sales_quantity']):
            try:
                df['date'] = pd.to_datetime(df['date'])
                df['month'] = df['date'].dt.month
                monthly_sales = df.groupby(['product_name', 'month'])['sales_quantity'].sum().unstack()
                monthly_sales = monthly_sales.fillna(0)
                
                for product in monthly_sales.index:
                    sales = monthly_sales.loc[product]
                    if sales.max() > 2 * sales.min():  # Significant variation
                        peak_month = sales.idxmax()
                        Notification.objects.create(
                            business=self.business,
                            message=f"Product {product} shows seasonal pattern with peak in month {peak_month}",
                            notification_type='seasonal_product'
                        )
            except Exception as e:
                print(f"Error generating seasonal products: {str(e)}")