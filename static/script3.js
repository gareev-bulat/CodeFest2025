document.addEventListener("DOMContentLoaded", function () {
    const healthForm = document.getElementById("healthForm");
    const resultText = document.getElementById("result");
    const chatLog = document.getElementById("chat-log");
    const chatbotForm = document.getElementById("chatbot-form");
    const chatbotInput = document.getElementById("chatbot-input");
    const spinner = document.getElementById("loadingSpinner");
    let predictionResult = null; // Store prediction result for chatbot

    healthForm.addEventListener("submit", function (event) {
        event.preventDefault();
        spinner.style.display = "block"; // Show loading spinner

        const formData = new FormData(this);
        const data = {};
        const numericFields = [
            "Age", "Gender", "AirPollution", "AlcoholUse", "DustAllergy", "OccupationalHazards",
            "GeneticRisk", "ChronicLungDisease", "BalancedDiet", "Obesity", "Smoking",
            "PassiveSmoker", "ChestPain", "CoughingOfBlood", "Fatigue", "WeightLoss",
            "ShortnessOfBreath", "Wheezing", "SwallowingDifficulty", "ClubbingOfFingerNails",
            "FrequentCold", "DryCough", "Snoring"
        ];

        formData.forEach((value, key) => {
            data[key] = numericFields.includes(key) ? parseFloat(value) : value;
        });

        console.log("Data being sent to backend:", data);

        fetch("/lung1", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(result => {
            if (result.error) {
                resultText.innerHTML = `<p>Error: ${result.error}</p>`;
            } else {
                predictionResult = result.prediction; // Store result for chatbot
                resultText.innerHTML = `Lung Cancer Risk Level: ${result.prediction}`;
                document.getElementById("chatbot").style.display = "block";
                chatLog.innerHTML += `<div class="bot-message">Health Suggestion: ${result.suggestions}</div>`;
            }
        })
        .catch(error => {
            console.error("Error:", error);
            resultText.innerHTML = "An error occurred. Please try again.";
        })
        .finally(() => {
            spinner.style.display = "none"; // Hide spinner after response
        });
    });

    chatbotForm.addEventListener("submit", function (e) {
        e.preventDefault();
        const userMessage = chatbotInput.value.trim();
        if (!userMessage) return;

        chatLog.innerHTML += `<div class="user-message">${userMessage}</div>`;
        chatbotInput.value = "";
        chatLog.innerHTML += `<div class="bot-message">Loading...</div>`;

        fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                message: userMessage,
                prediction: predictionResult
            })
        })
        .then(response => response.json())
        .then(data => {
            chatLog.querySelector(".bot-message:last-child").remove();
            if (data.error) {
                chatLog.innerHTML += `<div class="bot-message">Error: ${data.error}</div>`;
            } else {
                chatLog.innerHTML += `<div class="bot-message">${data.response}</div>`;
            }
        })
        .catch(error => {
            console.error("Error:", error);
            chatLog.innerHTML += `<div class="bot-message">Error: ${error.message}</div>`;

            
        });
    });
});
