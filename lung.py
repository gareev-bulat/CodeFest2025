from flask import Blueprint, request, jsonify, render_template
import tensorflow as tf
import pandas as pd
import joblib
import numpy as np
import os

lung_bp = Blueprint('lung1', __name__) 

class Lung:
    def __init__(self):
        """Initialize the Lung Cancer Prediction Model"""
        file_path = "cancer patient data sets.csv"
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        self.df = pd.read_csv(file_path)

        self.model_path = "lung_cancer_model.h5"
        self.scaler_path = "scaler1.pkl"

        try:
            self.model = tf.keras.models.load_model(self.model_path)
            self.scaler = joblib.load(self.scaler_path)
            print("Lung Cancer Model and Scaler Loaded Successfully!")
        except Exception as e:
            print(f"Error loading model or scaler: {e}")
            raise e

    def predict_risk(self, data):
        """Make lung cancer risk predictions"""
        required_features = [
            'Age', 'Gender', 'AirPollution', 'AlcoholUse', 'DustAllergy',
            'OccupationalHazards', 'GeneticRisk', 'ChronicLungDisease',
            'BalancedDiet', 'Obesity', 'Smoking', 'PassiveSmoker', 'ChestPain',
            'CoughingOfBlood', 'Fatigue', 'WeightLoss', 'ShortnessOfBreath',
            'Wheezing', 'SwallowingDifficulty', 'ClubbingOfFingerNails',
            'FrequentCold', 'DryCough', 'Snoring'
        ]

        if not all(feature in data for feature in required_features):
            missing_features = [feature for feature in required_features if feature not in data]
            print(f"Error: Missing features - {missing_features}")
            return {"error": f"Missing features: {missing_features}"}

        features = [data[feature] for feature in required_features]
        input_data = self.scaler.transform([features])
        prediction = self.model.predict(input_data)
        prediction_class = np.argmax(prediction)
        class_labels = {0: "Low", 1: "Medium", 2: "High"}
        return {"prediction": class_labels[prediction_class]}

lung_model = Lung()  

@lung_bp.route('/', methods=['GET', 'POST'])
def predict_lung():
    if request.method == 'POST':
        try:
            data = request.get_json()
            print("Received lung data:", data)
            result = lung_model.predict_risk(data)
            return jsonify(result), 200 if "prediction" in result else 400
        except Exception as e:
            print("Error during lung prediction:", str(e))
            return jsonify({"error": str(e)}), 500

    return render_template('lung1.html', top_players=lung_model.df.to_dict(orient='records'))

