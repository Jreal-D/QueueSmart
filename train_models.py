from models.ml_predictor import *
import pandas as pd

def main():
    print("QueueSmart ML Model Training Pipeline")
    print("=" * 50)
    
    # Load processed data
    df = pd.read_csv('data/processed_banking_data.csv')
    
    # Prepare data for ML
    X, y, encoders, feature_columns = prepare_ml_data(df)
    X_train, X_test, y_train, y_test = split_data(X, y)
    
    # Train different models
    models = {}
    results = []
    
    # 1. Linear Regression
    lr_model, lr_scaler = train_linear_regression(X_train, y_train)
    lr_results, lr_pred = evaluate_model(lr_model, X_test, y_test, "Linear Regression", lr_scaler)
    plot_predictions(y_test, lr_pred, "Linear Regression")
    models['linear_regression'] = (lr_model, lr_scaler)
    results.append(lr_results)
    
    # 2. Random Forest
    rf_model = train_random_forest(X_train, y_train)
    rf_results, rf_pred = evaluate_model(rf_model, X_test, y_test, "Random Forest")
    plot_predictions(y_test, rf_pred, "Random Forest")
    analyze_feature_importance(rf_model, feature_columns, "Random Forest")
    models['random_forest'] = (rf_model, None)
    results.append(rf_results)
    
    # 3. Gradient Boosting
    gb_model = train_gradient_boosting(X_train, y_train)
    gb_results, gb_pred = evaluate_model(gb_model, X_test, y_test, "Gradient Boosting")
    plot_predictions(y_test, gb_pred, "Gradient Boosting")
    analyze_feature_importance(gb_model, feature_columns, "Gradient Boosting")
    models['gradient_boosting'] = (gb_model, None)
    results.append(gb_results)
    
    # 4. Tuned Random Forest
    rf_tuned = tune_random_forest(X_train, y_train)
    rf_tuned_results, rf_tuned_pred = evaluate_model(rf_tuned, X_test, y_test, "Random Forest Tuned")
    models['random_forest_tuned'] = (rf_tuned, None)
    results.append(rf_tuned_results)
    
    # Compare all models
    print("\n" + "=" * 50)
    print("MODEL COMPARISON SUMMARY")
    print("=" * 50)
    
    results_df = pd.DataFrame(results)
    print(results_df.to_string(index=False))
    
    # Find best model
    best_model_idx = results_df['rmse'].idxmin()
    best_model_name = results_df.loc[best_model_idx, 'model_name']
    
    print(f"\nBest performing model: {best_model_name}")
    
    # Save best model
    if 'tuned' in best_model_name.lower():
        best_model, best_scaler = models['random_forest_tuned']
    elif 'random forest' in best_model_name.lower():
        best_model, best_scaler = models['random_forest']
    elif 'gradient' in best_model_name.lower():
        best_model, best_scaler = models['gradient_boosting']
    else:
        best_model, best_scaler = models['linear_regression']
    
    save_model(best_model, encoders, feature_columns, best_model_name, best_scaler)
    
    # Test prediction functionality
    print(f"\n" + "=" * 50)
    print("TESTING PREDICTION FUNCTIONALITY")
    print("=" * 50)
    
    # Load the saved model and test it
    model_filename = f'models/{best_model_name.lower().replace(" ", "_")}_model.joblib'
    loaded_model = load_model(model_filename)
    
    # Test prediction
    test_prediction = predict_wait_time(
        loaded_model,
        branch="Victoria Island",
        service_type="Transfer",
        hour=10,  # Peak hour
        day_of_week=1,  # Tuesday
        service_duration=5,
        current_queue_length=3
    )
    
    print(f"Test prediction: {test_prediction:.1f} minutes wait time")
    print("Model training pipeline completed successfully!")

if __name__ == "__main__":
    main()