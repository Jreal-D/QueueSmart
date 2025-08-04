import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def prepare_ml_data(df):
    """Prepare data for machine learning"""
    
    print("Preparing data for machine learning...")
    
    # Create a copy to avoid modifying original data
    ml_df = df.copy()
    
    # Convert categorical variables to numerical
    le_branch = LabelEncoder()
    le_service = LabelEncoder()
    
    ml_df['branch_encoded'] = le_branch.fit_transform(ml_df['branch'])
    ml_df['service_type_encoded'] = le_service.fit_transform(ml_df['service_type'])
    
    # Store encoders for later use
    encoders = {
        'branch': le_branch,
        'service_type': le_service
    }
    
    # Select features for prediction
    feature_columns = [
        'hour',
        'day_of_week', 
        'branch_encoded',
        'service_type_encoded',
        'service_duration_minutes',
        'queue_length_on_arrival',
        'is_peak_hour'
    ]
    
    # Convert boolean to int
    ml_df['is_peak_hour'] = ml_df['is_peak_hour'].astype(int)
    
    # Prepare feature matrix (X) and target vector (y)
    X = ml_df[feature_columns]
    y = ml_df['wait_time_minutes']
    
    print(f"Features selected: {feature_columns}")
    print(f"Dataset shape: {X.shape}")
    print(f"Target variable: wait_time_minutes")
    
    return X, y, encoders, feature_columns

def split_data(X, y, test_size=0.2, random_state=42):
    """Split data into training and testing sets"""
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )
    
    print(f"Training set: {X_train.shape[0]} samples")
    print(f"Testing set: {X_test.shape[0]} samples")
    
    return X_train, X_test, y_train, y_test

def train_linear_regression(X_train, y_train):
    """Train Linear Regression model"""
    
    print("Training Linear Regression model...")
    
    # Scale features for linear regression
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    
    model = LinearRegression()
    model.fit(X_train_scaled, y_train)
    
    return model, scaler

def train_random_forest(X_train, y_train):
    """Train Random Forest model"""
    
    print("Training Random Forest model...")
    
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42
    )
    
    model.fit(X_train, y_train)
    
    return model

def train_gradient_boosting(X_train, y_train):
    """Train Gradient Boosting model"""
    
    print("Training Gradient Boosting model...")
    
    model = GradientBoostingRegressor(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=6,
        random_state=42
    )
    
    model.fit(X_train, y_train)
    
    return model

def evaluate_model(model, X_test, y_test, model_name, scaler=None):
    """Evaluate model performance"""
    
    # Make predictions
    if scaler is not None:
        X_test_scaled = scaler.transform(X_test)
        y_pred = model.predict(X_test_scaled)
    else:
        y_pred = model.predict(X_test)
    
    # Calculate metrics
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    # Calculate accuracy within reasonable range (±5 minutes)
    accuracy_5min = np.mean(np.abs(y_test - y_pred) <= 5) * 100
    
    results = {
        'model_name': model_name,
        'rmse': rmse,
        'mae': mae,
        'r2_score': r2,
        'accuracy_5min': accuracy_5min
    }
    
    print(f"\n{model_name} Results:")
    print(f"  RMSE: {rmse:.2f} minutes")
    print(f"  MAE: {mae:.2f} minutes")
    print(f"  R² Score: {r2:.3f}")
    print(f"  Accuracy within 5 min: {accuracy_5min:.1f}%")
    
    return results, y_pred

def plot_predictions(y_test, y_pred, model_name):
    """Plot actual vs predicted values"""
    
    plt.figure(figsize=(10, 6))
    
    plt.subplot(1, 2, 1)
    plt.scatter(y_test, y_pred, alpha=0.5)
    plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
    plt.xlabel('Actual Wait Time (minutes)')
    plt.ylabel('Predicted Wait Time (minutes)')
    plt.title(f'{model_name}: Actual vs Predicted')
    
    plt.subplot(1, 2, 2)
    residuals = y_test - y_pred
    plt.scatter(y_pred, residuals, alpha=0.5)
    plt.axhline(y=0, color='r', linestyle='--')
    plt.xlabel('Predicted Wait Time (minutes)')
    plt.ylabel('Residuals')
    plt.title(f'{model_name}: Residual Plot')
    
    plt.tight_layout()
    plt.savefig(f'models/{model_name.lower().replace(" ", "_")}_results.png')
    plt.show()

def analyze_feature_importance(model, feature_columns, model_name):
    """Analyze feature importance for tree-based models"""
    
    if hasattr(model, 'feature_importances_'):
        importance_df = pd.DataFrame({
            'feature': feature_columns,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print(f"\n{model_name} Feature Importance:")
        for _, row in importance_df.iterrows():
            print(f"  {row['feature']}: {row['importance']:.3f}")
        
        # Plot feature importance
        plt.figure(figsize=(10, 6))
        sns.barplot(data=importance_df, x='importance', y='feature')
        plt.title(f'{model_name} Feature Importance')
        plt.xlabel('Importance Score')
        plt.tight_layout()
        plt.savefig(f'models/{model_name.lower().replace(" ", "_")}_importance.png')
        plt.show()
        
        return importance_df
    else:
        print(f"{model_name} does not support feature importance analysis")
        return None

def tune_random_forest(X_train, y_train):
    """Tune Random Forest hyperparameters"""
    
    print("Tuning Random Forest hyperparameters...")
    
    param_grid = {
        'n_estimators': [50, 100, 200],
        'max_depth': [5, 10, 15, None],
        'min_samples_split': [2, 5, 10],
        'min_samples_leaf': [1, 2, 4]
    }
    
    rf = RandomForestRegressor(random_state=42)
    
    grid_search = GridSearchCV(
        rf, param_grid, cv=5, 
        scoring='neg_mean_squared_error',
        n_jobs=-1, verbose=1
    )
    
    grid_search.fit(X_train, y_train)
    
    print(f"Best parameters: {grid_search.best_params_}")
    print(f"Best cross-validation score: {-grid_search.best_score_:.2f}")
    
    return grid_search.best_estimator_

def save_model(model, encoders, feature_columns, model_name, scaler=None):
    """Save trained model and associated data"""
    
    model_data = {
        'model': model,
        'encoders': encoders,
        'feature_columns': feature_columns,
        'scaler': scaler,
        'model_name': model_name,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    filename = f'models/{model_name.lower().replace(" ", "_")}_model.joblib'
    joblib.dump(model_data, filename)
    
    print(f"Model saved to {filename}")
    return filename

def load_model(filename):
    """Load saved model"""
    
    model_data = joblib.load(filename)
    
    print(f"Loaded {model_data['model_name']} model")
    print(f"Trained on: {model_data['timestamp']}")
    
    return model_data

def predict_wait_time(model_data, branch, service_type, hour, day_of_week, 
                     service_duration, current_queue_length):
    """Make wait time prediction using loaded model"""
    
    # Prepare input data
    input_data = pd.DataFrame({
        'hour': [hour],
        'day_of_week': [day_of_week],
        'branch_encoded': [model_data['encoders']['branch'].transform([branch])[0]],
        'service_type_encoded': [model_data['encoders']['service_type'].transform([service_type])[0]],
        'service_duration_minutes': [service_duration],
        'queue_length_on_arrival': [current_queue_length],
        'is_peak_hour': [1 if hour in [9, 10, 11, 13, 14, 15] else 0]
    })
    
    # Make prediction
    if model_data['scaler'] is not None:
        input_scaled = model_data['scaler'].transform(input_data)
        prediction = model_data['model'].predict(input_scaled)[0]
    else:
        prediction = model_data['model'].predict(input_data)[0]
    
    return max(0, prediction)  # Ensure non-negative prediction