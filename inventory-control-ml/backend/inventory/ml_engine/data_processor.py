import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer

class DataProcessor:
    def __init__(self, file_path):
        self.file_path = file_path
    
    def load_data(self, only_preview=False):
        """Load and optionally preprocess data"""
        if self.file_path.endswith('.csv'):
            df = pd.read_csv(self.file_path)
        else:
            raise ValueError("Only CSV files are supported")
        
        return df if only_preview else self._preprocess_data(df)
    
    def _preprocess_data(self, df):
        """Full preprocessing for ML"""
        df = self._handle_missing_values(df)
        df = self._convert_date_columns(df)
        df = self._encode_categorical(df)
        df = self._scale_numerical(df)
        return df
    
    def _handle_missing_values(self, df):
        num_cols = df.select_dtypes(include=np.number).columns
        if not num_cols.empty:
            imputer = SimpleImputer(strategy='median')
            df[num_cols] = imputer.fit_transform(df[num_cols])
        
        cat_cols = df.select_dtypes(include=['object']).columns
        if not cat_cols.empty:
            imputer = SimpleImputer(strategy='most_frequent')
            df[cat_cols] = imputer.fit_transform(df[cat_cols])
        
        return df
    
    def _convert_date_columns(self, df):
        for col in df.columns:
            if df[col].dtype == 'object':
                try:
                    df[col] = pd.to_datetime(df[col])
                except:
                    pass
        return df
    
    def _encode_categorical(self, df):
        cat_cols = df.select_dtypes(include=['object']).columns
        for col in cat_cols:
            if df[col].nunique() < 10:
                df = pd.get_dummies(df, columns=[col], prefix=[col])
        return df
    
    def _scale_numerical(self, df):
        num_cols = df.select_dtypes(include=np.number).columns
        if not num_cols.empty:
            scaler = StandardScaler()
            df[num_cols] = scaler.fit_transform(df[num_cols])
        return df