import tensorflow as tf
import pandas as pd
import numpy as np
from tensorflow import keras
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score
import joblib

file = "diabetes_dataset.csv"
df = pd.read_csv(file)

print(df.head())
print(df.info())  
print(df.isnull().sum()) 
df = df.dropna() 

required_features = [
    'Age', 'Pregnancies', 'BMI', 'Glucose', 'BloodPressure', 'HbA1c', 'LDL', 'HDL',
    'Triglycerides', 'WaistCircumference', 'HipCircumference', 'WHR', 'FamilyHistory',
    'DietType', 'Hypertension', 'MedicationUse', 'Outcome'
]


if not all(feature in df.columns for feature in required_features):
    raise ValueError("Dataset is missing required features.")


X = df.drop(columns=["Outcome"])  
y = df["Outcome"] 


scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)  

joblib.dump(scaler, "scaler.pkl")


X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

model = keras.Sequential([
    keras.layers.Dense(64, activation='relu', input_shape=(X_train.shape[1],)),
    keras.layers.Dense(32, activation='relu'),
    keras.layers.Dense(1, activation='sigmoid')  
])

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

model.fit(X_train, y_train, epochs=10, batch_size=32, validation_split=0.2)


y_pred = (model.predict(X_test) > 0.5).astype(int) 
accuracy = accuracy_score(y_test, y_pred)

print(f"Model Accuracy: {accuracy:.2f}")

model.save("health_model.h5")
print("Model saved successfully!")