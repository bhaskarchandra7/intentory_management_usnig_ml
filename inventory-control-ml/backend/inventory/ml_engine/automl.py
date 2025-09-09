import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_absolute_error
from tpot import TPOTClassifier, TPOTRegressor
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
import joblib
import os
import tempfile

class AutoMLEngine:
    def __init__(self, dataset_path):
        self.dataset_path = dataset_path
        self.df = pd.read_csv(dataset_path)
        
    def train(self):
        if 'target' not in self.df.columns:
            raise ValueError("Dataset must contain 'target' column")
            
        X = self.df.drop('target', axis=1)
        y = self.df['target']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
        
        # Determine problem type
        if y.dtype == 'object':
            problem_type = 'classification'
            model = TPOTClassifier(generations=3, population_size=10, verbosity=2)
            metric = accuracy_score
        else:
            problem_type = 'regression'
            model = TPOTRegressor(generations=3, population_size=10, verbosity=2)
            metric = mean_absolute_error
        
        model.fit(X_train, y_train)
        score = metric(y_test, model.predict(X_test))
        
        model_path = os.path.join(tempfile.gettempdir(), 'model.joblib')
        joblib.dump(model.fitted_pipeline_, model_path)
        
        return {
            'best_model_type': problem_type,
            'best_algorithm': str(model.fitted_pipeline_),
            'best_accuracy': score,
            'model_file': model_path
        }
    
    def predict(self, model_path, input_data):
        model = joblib.load(model_path)
        input_df = pd.DataFrame([input_data])
        return model.predict(input_df).tolist()