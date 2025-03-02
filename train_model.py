import tensorflow as tf
import pandas as pd
import numpy as np
from tensorflow import keras
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score
import joblib

# Load dataset (Update with your actual file path)
file = "diabetes_dataset.csv"
df = pd.read_csv(file)

# Check dataset structure
print(df.head())  # View first few rows
print(df.info())  # General info about data types
print(df.isnull().sum())  # Count missing values in each column
df = df.dropna()  # Remove rows with missing values

# Ensure the dataset has the same features as expected in app.py
required_features = [
    'Age', 'Pregnancies', 'BMI', 'Glucose', 'BloodPressure', 'HbA1c', 'LDL', 'HDL',
    'Triglycerides', 'WaistCircumference', 'HipCircumference', 'WHR', 'FamilyHistory',
    'DietType', 'Hypertension', 'MedicationUse', 'Outcome'
]

# Check if all required features are present in the dataset
if not all(feature in df.columns for feature in required_features):
    raise ValueError("Dataset is missing required features.")

# Define features (X) and target (y)
X = df.drop(columns=["Outcome"])  # Features
y = df["Outcome"]  # Labels

# Normalize features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)  # Normalize the features

# Save the fitted scaler for later use
joblib.dump(scaler, "scaler.pkl")

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

# Train the model (TensorFlow/Keras model)
model = keras.Sequential([
    keras.layers.Dense(64, activation='relu', input_shape=(X_train.shape[1],)),
    keras.layers.Dense(32, activation='relu'),
    keras.layers.Dense(1, activation='sigmoid')  # Binary classification
])

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# Train the model
model.fit(X_train, y_train, epochs=10, batch_size=32, validation_split=0.2)

# Make predictions
y_pred = (model.predict(X_test) > 0.5).astype(int)  # Convert probabilities to binary predictions
accuracy = accuracy_score(y_test, y_pred)

print(f"Model Accuracy: {accuracy:.2f}")

# Save the trained model
model.save("health_model.h5")
print("Model saved successfully!")