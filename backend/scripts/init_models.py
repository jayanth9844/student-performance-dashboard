#!/usr/bin/env python3
"""
Model initialization script for Render deployment
Creates dummy models if real models are not available during deployment
"""

import os
import joblib
import numpy as np
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

def create_dummy_models():
    """Create dummy models for deployment when real models are not available"""
    
    # Ensure models directory exists
    models_dir = Path(__file__).parent.parent / "app" / "models"
    models_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Creating dummy models in {models_dir}")
    
    # Generate dummy training data
    np.random.seed(42)
    n_samples = 1000
    n_features = 5
    
    # Feature names: comprehension, attention, focus, retention, engagement_time
    X = np.random.rand(n_samples, n_features) * 100
    y_regression = np.random.rand(n_samples) * 100  # Assignment scores 0-100
    
    # Create and fit scaler
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Create and fit regression model
    regression_model = RandomForestRegressor(
        n_estimators=50,
        max_depth=10,
        random_state=42,
        n_jobs=1  # Single job for free tier
    )
    regression_model.fit(X_scaled, y_regression)
    
    # Create and fit clustering model
    clustering_model = KMeans(
        n_clusters=4,
        random_state=42,
        n_init=10,
        max_iter=100
    )
    clustering_model.fit(X_scaled)
    
    # Save models
    model_files = {
        "model.joblib": regression_model,
        "cluster_model.joblib": clustering_model,
        "kmeans_model.joblib": clustering_model,  # Alternative name for compatibility
        "scaler.pkl": scaler
    }
    
    for filename, model in model_files.items():
        filepath = models_dir / filename
        joblib.dump(model, filepath)
        print(f"Saved {filename} to {filepath}")
    
    print("Dummy models created successfully!")
    return True

def check_models_exist():
    """Check if model files exist"""
    models_dir = Path(__file__).parent.parent / "app" / "models"
    required_files = ["model.joblib", "cluster_model.joblib", "scaler.pkl"]
    
    missing_files = []
    for filename in required_files:
        filepath = models_dir / filename
        if not filepath.exists():
            missing_files.append(filename)
    
    return len(missing_files) == 0, missing_files

def main():
    """Main initialization function"""
    print("Initializing models for deployment...")
    
    models_exist, missing_files = check_models_exist()
    
    if models_exist:
        print("All model files found. No initialization needed.")
        return True
    
    print(f"Missing model files: {missing_files}")
    print("Creating dummy models for deployment...")
    
    try:
        return create_dummy_models()
    except Exception as e:
        print(f"Error creating dummy models: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
