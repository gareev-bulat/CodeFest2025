from flask import Flask, request, jsonify, render_template
import tensorflow as tf
import joblib
import os
import json
import requests
import openai 
import pandas as pd
from dotenv import load_dotenv
from lung import lung_bp
app = Flask(__name__)
app.register_blueprint(lung_bp, url_prefix="/lung")

# Load environment variables and set API key for OpenAI
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = openai_api_key

# Load the model and scaler
model_path = os.path.join(os.getcwd(), "health_model.h5")
scaler_path = os.path.join(os.getcwd(), "scaler.pkl")

try:
    model = tf.keras.models.load_model(model_path)
    scaler = joblib.load(scaler_path)
    print("Model and scaler loaded successfully!")
except Exception as e:
    print(f"Error loading model or scaler: {e}")
    raise e

def get_chat_completion(prompt):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {openai.api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant providing health suggestions."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()
@app.route('/chat', methods=['POST'])
def chat():
    try:
        # Get user input and prediction from request
        user_input = request.json.get('message')
        prediction = request.json.get('prediction')  # Prediction from the AI model
        print("Received user input:", user_input)  # Log the user input
        print("Received prediction:", prediction)  # Log the prediction

        # Prepare the prompt for OpenAI API
        prompt = f"The user is at {'High Risk' if prediction == 1 else 'Low Risk'} for diabetes. {user_input}"
        chat_response = get_chat_completion(prompt)

        # Extract the chatbot response
        if "choices" in chat_response and len(chat_response["choices"]) > 0:
            chatbot_response = chat_response["choices"][0]["message"].get("content", "No response provided.")
        else:
            chatbot_response = "No response provided."

        # Return the chatbot response
        return jsonify({"response": chatbot_response})

    except Exception as e:
        print("Error during chat:", str(e))  # Log the exception
        return jsonify({"error": str(e)}), 500
@app.route('/')
def home():
    return render_template('welcome.html')

@app.route('/diabetes_prediction')
def diabetes_prediction():
    return render_template('diabetes_prediction.html')

@app.route('/lung')


def prediction2():
    return render_template('lung1.html')

@app.route('/prediction3')
def prediction():
    return render_template('prediction3.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        # Complete list of features used during scaler fit
        required_features = [
            'Age', 'Pregnancies', 'BMI', 'Glucose', 'BloodPressure', 'HbA1c',
            'LDL', 'HDL', 'Triglycerides', 'WaistCircumference', 'HipCircumference', 'WHR',
            'FamilyHistory', 'DietType', 'Hypertension', 'MedicationUse'
        ]
        
        # Define default values for features missing from the form (HDL & Triglycerides)
        defaults = {
            'HDL': 50,           # default HDL value; adjust as needed
            'Triglycerides': 150 # default Triglycerides value; adjust as needed
        }
        
        features = []
        missing_fields = []
        
        for feature in required_features:
            if feature in data and data[feature] != "":
                try:
                    value = float(data[feature])
                except ValueError:
                    return jsonify({"error": f"Invalid input for {feature}. Must be numeric."}), 400
            elif feature in defaults:
                value = defaults[feature]
            else:
                missing_fields.append(feature)
                continue
            features.append(value)
        
        if missing_fields:
            return jsonify({"error": f"Missing fields: {', '.join(missing_fields)}"}), 400

        # Convert to DataFrame with feature names to match scaler expectations
        input_df = pd.DataFrame([features], columns=required_features)
        input_data = scaler.transform(input_df)
        prediction = model.predict(input_data)
        prediction_binary = int(prediction[0][0] > 0.5)
        json_result = json.dumps({"prediction": prediction_binary})

        # Get chatbot suggestions
        prompt = f"Give me health suggestions based on my results: {json_result}"
        chat_response = get_chat_completion(prompt)
        if "choices" in chat_response and len(chat_response["choices"]) > 0:
            suggestions = chat_response["choices"][0]["message"].get("content", "No suggestions provided.")
        else:
            suggestions = "No suggestions provided."
        
        # Format suggestions: split into sentences and wrap each in a <p> tag
        sentences = [s.strip() for s in suggestions.split(".") if s.strip()]
        formatted_suggestions = "".join([f"<p>{s}.</p>" for s in sentences])
        
        return jsonify({
            "prediction": prediction_binary,
            "suggestions": formatted_suggestions
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=2700)
