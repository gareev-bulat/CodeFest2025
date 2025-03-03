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
app.register_blueprint(lung_bp, url_prefix="/lung1")

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = openai_api_key


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
        user_input = request.json.get('message')
        prediction = request.json.get('prediction')  
        print("Received user input:", user_input)  
        print("Received prediction:", prediction) 

      
        prompt = f"The user is at {'High Risk' if prediction == 1 else 'Low Risk'} for diabetes. {user_input}"
        chat_response = get_chat_completion(prompt)

        if "choices" in chat_response and len(chat_response["choices"]) > 0:
            chatbot_response = chat_response["choices"][0]["message"].get("content", "No response provided.")
        else:
            chatbot_response = "No response provided."

        return jsonify({"response": chatbot_response})

    except Exception as e:
        print("Error during chat:", str(e))  
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
        required_features = [
            'Age', 'Pregnancies', 'BMI', 'Glucose', 'BloodPressure', 'HbA1c',
            'LDL', 'HDL', 'Triglycerides', 'WaistCircumference', 'HipCircumference', 'WHR',
            'FamilyHistory', 'DietType', 'Hypertension', 'MedicationUse'
        ]
        
        defaults = {
            'HDL': 50,           
            'Triglycerides': 150 
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

        input_df = pd.DataFrame([features], columns=required_features)
        input_data = scaler.transform(input_df)
        prediction = model.predict(input_data)
        prediction_binary = int(prediction[0][0] > 0.5)
        json_result = json.dumps({"prediction": prediction_binary})

        prompt = f"Give me health suggestions based on my results: {json_result}"
        chat_response = get_chat_completion(prompt)
        if "choices" in chat_response and len(chat_response["choices"]) > 0:
            suggestions = chat_response["choices"][0]["message"].get("content", "No suggestions provided.")
        else:
            suggestions = "No suggestions provided."
        
        sentences = [s.strip() for s in suggestions.split(".") if s.strip()]
        formatted_suggestions = "".join([f"<p>{s}.</p>" for s in sentences])
        
        return jsonify({
            "prediction": prediction_binary,
            "suggestions": formatted_suggestions
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=2702)
