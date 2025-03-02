import tensorflow as tf
import pandas as pd
import numpy as np
from tensorflow import keras
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score
import joblib

file = "cancer patient data sets.csv"
df = pd.read_csv(file)

df = df.drop(columns=['index', 'Patient Id'])

df.columns = df.columns.str.strip()  # Remove leading/trailing spaces

required_features = [
    'Age', 'Gender', 'Air Pollution', 'Alcohol use', 'Dust Allergy',
    'OccuPational Hazards', 'Genetic Risk', 'chronic Lung Disease',
    'Balanced Diet', 'Obesity', 'Smoking', 'Passive Smoker', 'Chest Pain',
    'Coughing of Blood', 'Fatigue', 'Weight Loss', 'Shortness of Breath',
    'Wheezing', 'Swallowing Difficulty', 'Clubbing of Finger Nails',
    'Frequent Cold', 'Dry Cough', 'Snoring'
]
target_column = 'Level'  # Cancer severity (Low, Medium, High)

if not all(feature in df.columns for feature in required_features + [target_column]):
    raise ValueError("Dataset is missing required features.")

encoder = LabelEncoder()
df['Gender'] = encoder.fit_transform(df['Gender'])  # Convert Gender (Male=1, Female=0)
df[target_column] = encoder.fit_transform(df[target_column])  # Encode 'Level' (Low=0, Medium=1, High=2)

X = df[required_features]
y = df[target_column]

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

joblib.dump(scaler, "scaler1.pkl")

X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

model = keras.Sequential([
    keras.layers.Dense(64, activation='relu', input_shape=(X_train.shape[1],)),
    keras.layers.Dense(32, activation='relu'),
    keras.layers.Dense(3, activation='softmax')  # Multi-class classification (3 categories)
])

model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

model.fit(X_train, y_train, epochs=15, batch_size=32, validation_split=0.2)

y_pred = np.argmax(model.predict(X_test), axis=1)  # Convert probabilities to class labels

accuracy = accuracy_score(y_test, y_pred)
print(f"Model Accuracy: {accuracy:.2f}")

model.save("lung_cancer_model.h5")
print("Model saved successfully!")