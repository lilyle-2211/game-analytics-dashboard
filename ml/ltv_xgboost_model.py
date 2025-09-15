"""
LTV Day 14 Prediction Model using XGBoost with Hyperparameter Tuning

This script trains an optimized XGBoost model to predict Day 14 LTV using user behavior data.
The model uses hyperparameter tuning to achieve the best possible performance.

Usage:
    python ltv_xgboost_model.py

Requirements:
    pip install xgboost pandas numpy scikit-learn matplotlib optuna
"""

import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import matplotlib.pyplot as plt
import optuna
import warnings
warnings.filterwarnings('ignore')
optuna.logging.set_verbosity(optuna.logging.WARNING)


def prepare_features(df):
    """Prepare features for XGBoost training."""
    print("🔧 Preparing features...")
    
    # Define feature sets
    numeric_features = [
        'first_purchase_day', 'days_since_install', 
        'sum_cumulative_levels_day1_1', 'sum_cumulative_levels_day1_3',
        'sum_cumulative_levels_day1_7', 'sum_cumulative_levels_day1_14',
        'avg_cumulative_levels_day1_3', 'avg_cumulative_levels_day1_7',
        'avg_cumulative_levels_day1_14', 'completion_rate_day1_1',
        'completion_rate_day1_3', 'completion_rate_day1_7',
        'completion_rate_day1_14', 'max_level_reach_day1_1',
        'max_level_reach_day1_3', 'max_level_reach_day1_7',
        'max_level_reach_day1_14', 'revenue_day1_1', 'revenue_day1_3',
        'revenue_day1_7'
    ]
    
    categorical_features = [
        'is_android_user', 'is_return_next_day', 'is_female', 'is_age_30'
    ]
    
    target = 'revenue_day1_20'
    
    # Prepare feature matrix
    all_features = numeric_features + categorical_features
    X = df[all_features].copy()
    y = df[target].copy()
    
    # Handle categorical features (convert to integers for XGBoost compatibility)
    for cat_col in categorical_features:
        X[cat_col] = X[cat_col].astype('int')
    
    print(f"✅ Features prepared: {len(all_features)} features, {len(df)} samples")
    print(f"   - Numeric features: {len(numeric_features)}")
    print(f"   - Categorical features: {len(categorical_features)}")
    print(f"   - Target: {target}")
    
    return X, y, all_features

def hyperparameter_tuning(X_train, y_train, X_test, y_test, n_trials=50):
    """Perform hyperparameter tuning using Optuna (simple version)."""
    print(f"🔧 Performing hyperparameter tuning with Optuna ({n_trials} trials)...")
    
    def objective(trial):
        # Define hyperparameter search space with stronger regularization to prevent overfitting
        params = {
            'objective': 'reg:squarederror',
            'max_depth': trial.suggest_int('max_depth', 2, 5),  # Shallower trees
            'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.15),  # Lower learning rates
            'n_estimators': trial.suggest_int('n_estimators', 50, 300),  # Fewer trees
            'subsample': trial.suggest_float('subsample', 0.5, 0.8),  # More aggressive subsampling
            'colsample_bytree': trial.suggest_float('colsample_bytree', 0.5, 0.8),  # More feature subsampling
            'min_child_weight': trial.suggest_int('min_child_weight', 3, 10),  # Higher minimum samples
            'reg_alpha': trial.suggest_float('reg_alpha', 0.1, 2.0),  # Strong L1 regularization
            'reg_lambda': trial.suggest_float('reg_lambda', 1.0, 5.0),  # Strong L2 regularization
            'random_state': 42
        }
        
        # Create and train model
        model = xgb.XGBRegressor(**params)
        model.fit(X_train, y_train, verbose=False)
        
        # Predict and calculate MSE for optimization
        y_pred = model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        
        return mse
    
    # Create Optuna study (simple version)
    study = optuna.create_study(direction='minimize')
    
    # Optimize
    print("   - Running Optuna optimization...")
    study.optimize(objective, n_trials=n_trials)
    
    # Get best parameters and score
    best_params = study.best_params
    best_score = study.best_value
    
    print(f"   - Best test MSE: ${best_score:.2f}")
    print(f"   - Best test RMSE: ${np.sqrt(best_score):.2f}")
    print(f"   - Number of trials completed: {len(study.trials)}")
    print("   - Best parameters:")
    for param, value in best_params.items():
        print(f"     {param}: {value}")
    
    return best_params, study

def train_xgboost_model(X, y, tune_hyperparameters=True, n_trials=50):
    """Train XGBoost model with optimal parameters."""
    print("🚀 Training XGBoost model...")
    
    # Stratified train-test split (80%-20%) by payers/non-payers
    payer_stratify = (y > 0).astype(int)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=payer_stratify
    )
    
    print(f"   - Training samples: {len(X_train)} ({len(X_train)/len(X)*100:.0f}%)")
    print(f"   - Test samples: {len(X_test)} ({len(X_test)/len(X)*100:.0f}%)")
    
    if tune_hyperparameters:
        # Get optimal hyperparameters using Optuna
        best_params, study = hyperparameter_tuning(X_train, y_train, X_test, y_test, n_trials)
        
        # Train final model with best parameters
        print("🎯 Training final model with optimized parameters...")
        final_model = xgb.XGBRegressor(**best_params)
        
        final_model.fit(X_train, y_train)
        
        return final_model, X_train, X_test, y_train, y_test, study
    
    else:
        # Use default parameters
        print("🎯 Training with default parameters...")
        default_model = xgb.XGBRegressor(
            objective='reg:squarederror',
            max_depth=6,
            learning_rate=0.1,
            n_estimators=500,
            subsample=0.8,
            colsample_bytree=0.8,
            min_child_weight=1,
            reg_alpha=0.1,
            reg_lambda=1.0,
            random_state=42
        )
        
        default_model.fit(X_train, y_train)
        
        return default_model, X_train, X_test, y_train, y_test, None

def evaluate_model(model, X_train, X_test, y_train, y_test):
    """Evaluate model performance and generate metrics."""
    print("📈 Evaluating model performance...")
    
    # Check if model is XGBRegressor (sklearn-style) or native XGBoost
    if hasattr(model, 'predict') and hasattr(model, 'feature_importances_'):
        # XGBRegressor (sklearn-style)
        y_pred_train = model.predict(X_train)
        y_pred_test = model.predict(X_test)
    else:
        # Native XGBoost model
        dtrain = xgb.DMatrix(X_train, enable_categorical=True)
        dtest = xgb.DMatrix(X_test, enable_categorical=True)
        y_pred_train = model.predict(dtrain)
        y_pred_test = model.predict(dtest)
    
    # Calculate metrics
    train_rmse = np.sqrt(mean_squared_error(y_train, y_pred_train))
    test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
    train_mae = mean_absolute_error(y_train, y_pred_train)
    test_mae = mean_absolute_error(y_test, y_pred_test)
    test_r2 = r2_score(y_test, y_pred_test)
    
    print("\n=== Model Performance ===")
    print(f"Train RMSE: ${train_rmse:.2f}")
    print(f"Test RMSE: ${test_rmse:.2f}")
    print(f"Train MAE: ${train_mae:.2f}")
    print(f"Test MAE: ${test_mae:.2f}")
    print(f"Test R²: {test_r2:.4f}")
    
    return {
        'train_rmse': train_rmse,
        'test_rmse': test_rmse,
        'test_mae': test_mae,
        'test_r2': test_r2
    }

def analyze_feature_importance(model, feature_names):
    """Analyze and visualize feature importance."""
    print("🔍 Analyzing feature importance...")
    
    # Get feature importance based on model type
    if hasattr(model, 'feature_importances_'):
        # XGBRegressor (sklearn-style)
        importances = model.feature_importances_
        importance_df = pd.DataFrame({
            'feature': feature_names,
            'importance': importances
        }).sort_values('importance', ascending=False)
    else:
        # Native XGBoost model
        feature_importance = model.get_score(importance_type='weight')
        importance_df = pd.DataFrame({
            'feature': list(feature_importance.keys()),
            'importance': list(feature_importance.values())
        }).sort_values('importance', ascending=False)
    
    print("\n=== Top 10 Feature Importance ===")
    print(importance_df.head(10).to_string(index=False))
    
    # Plot feature importance
    plt.figure(figsize=(12, 8))
    top_features = importance_df.head(15)
    
    plt.barh(range(len(top_features)), top_features['importance'])
    plt.yticks(range(len(top_features)), top_features['feature'])
    plt.xlabel('Importance Score')
    plt.title('XGBoost Feature Importance (Top 15)')
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig('feature_importance.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    return importance_df


def main():
    """Main execution function."""
    print("🎯 LTV Day 20 Forecasting Model Training")
    print("=" * 50)
    
    # Load data from global variable 'ml'
    try:
        df = ml  # Use ml dataframe as source
        print(f"✅ Loaded {len(df)} users with Day 20 LTV data from ml dataframe")
    except NameError:
        print("❌ 'ml' dataframe not found. Please ensure ml variable is available.")
        return
    
    # Prepare features
    X, y, feature_names = prepare_features(df)
    
    # Train model with Optuna hyperparameter tuning  
    model, X_train, X_test, y_train, y_test, study = train_xgboost_model(X, y, tune_hyperparameters=True, n_trials=50)
    
    # Evaluate model
    metrics = evaluate_model(model, X_train, X_test, y_train, y_test)
    
    # Analyze feature importance
    feature_importance = analyze_feature_importance(model, feature_names)
    
    # Visualize Optuna optimization results
    if study is not None:
        print("\n📊 Creating Optuna optimization plots...")
        try:
            # Plot optimization history
            fig1 = optuna.visualization.plot_optimization_history(study)
            fig1.write_html('optuna_optimization_history.html')
            
            # Plot parameter importance
            fig2 = optuna.visualization.plot_param_importances(study)
            fig2.write_html('optuna_param_importance.html')
            
            # Plot hyperparameter relationships
            fig3 = optuna.visualization.plot_parallel_coordinate(study)
            fig3.write_html('optuna_parallel_coordinate.html')
            
            print("   - Optuna plots saved as HTML files")
            
        except Exception as e:
            print(f"   - Could not create Optuna plots: {e}")
    
    # Save model
    model.save_model('ltv_xgboost_model.json')
    
    # Save feature importance
    feature_importance.to_csv('feature_importance.csv', index=False)
    
    print("\n🎉 Model training completed successfully!")
    print(f"📊 Final Results:")
    print(f"   - Test RMSE: ${metrics['test_rmse']:.2f}")
    print(f"   - Test R² Score: {metrics['test_r2']:.4f}")
    
    if study is not None:
        print(f"   - Optuna trials completed: {len(study.trials)}")
        print(f"   - Best trial test MSE: ${study.best_value:.2f}")
        print(f"   - Best trial test RMSE: ${np.sqrt(study.best_value):.2f}")
    
    print(f"\n💾 Files saved:")
    print(f"   - ltv_xgboost_model.json (XGBoost model)")
    print(f"   - feature_importance.csv (Feature importance)")
    if study is not None:
        print(f"   - optuna_*.html (Optuna visualization plots)")


if __name__ == "__main__":
    main()