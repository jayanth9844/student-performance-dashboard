import os
import joblib
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.linear_model import LinearRegression

# Import constants (ensure these paths are correctly defined in train_utils.py)
from train_utils import DATA_FILE_PATH, MODEL_DIR, MODEL_PATH


df = pd.read_csv(DATA_FILE_PATH)  
features = ["comprehension", "attention", "focus", "retention", "engagement_time"]
target = "assessment_score"

X = df[features]
y = df[target]


X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)


model = LinearRegression()
model.fit(X_train_scaled, y_train)

y_pred = model.predict(X_test_scaled)
r2 = r2_score(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
cv_score = np.mean(cross_val_score(model, X, y, cv=5))

print(f"✅ R² Score: {r2:.3f}")
print(f"✅ RMSE: {rmse:.3f}")
print(f"✅ Cross-Validation Score: {cv_score:.3f}")


os.makedirs(MODEL_DIR, exist_ok=True)
joblib.dump(model, MODEL_PATH)  
joblib.dump(scaler, os.path.join(MODEL_DIR, "scaler.pkl"))  
print(f"📁 Model saved at: {MODEL_PATH}")
print(f"📁 Scaler saved at: {os.path.join(MODEL_DIR, 'scaler.pkl')}")
