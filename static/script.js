
document.addEventListener('DOMContentLoaded', function () {
    const healthForm = document.getElementById('healthForm');
    const predictionText = document.getElementById('predictionText');
    const suggestionsContainer = document.getElementById('suggestionsContainer');
    const spinner = document.getElementById('loadingSpinner');
    const chatLog = document.getElementById('chat-log');
    const chatbotForm = document.getElementById('chatbot-form');
    const chatbotInput = document.getElementById('chatbot-input');
  
    let predictionResult = null; 
  
    healthForm.addEventListener('submit', function (e) {
        e.preventDefault();
        spinner.style.display = 'block';
        const formData = new FormData(healthForm);
        const data = {};
        formData.forEach((value, key) => {
            data[key] = value;
        });
  
        fetch('/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
     
        .then(data => {
            if (data.error) {
                predictionText.innerHTML = `<p>Error: ${data.error}</p>`;
                suggestionsContainer.innerHTML = "";
            } else {
                predictionText.innerHTML = `<strong>Prediction:</strong> ${data.prediction === 1 ? 'High Risk of Diabetes' : 'Low Risk of Diabetes'}`;
                suggestionsContainer.innerHTML = `<h3>Health Suggestions:</h3>${data.suggestions}`;
        
                
                predictionResult = data.prediction;
        
                document.getElementById('chatbot').style.display = 'block';
        
                const chatLog = document.getElementById('chat-log');
                chatLog.innerHTML += `<div class="bot-message">${data.suggestions}</div>`;
        
                chatLog.scrollTop = chatLog.scrollHeight;
            }
        })
       
        .catch(error => {
            console.error('Error:', error);
            predictionText.innerHTML = `<p>Error: ${error}</p>`;
        })
        .finally(() => {
            spinner.style.display = 'none';
        });
    });
  
    chatbotForm.addEventListener('submit', function (e) {
        e.preventDefault();
        const userMessage = chatbotInput.value.trim();
        if (!userMessage) return;
  
        chatLog.innerHTML += `<div class="user-message">${userMessage}</div>`;
        chatbotInput.value = '';
  
        chatLog.innerHTML += `<div class="bot-message">Loading...</div>`;
  
        fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: userMessage,
                prediction: predictionResult
            })
        })
        .then(response => response.json())
        .then(data => {
            chatLog.querySelector('.bot-message:last-child').remove();
            if (data.error) {
                chatLog.innerHTML += `<div class="bot-message">Error: ${data.error}</div>`;
            } else {
                chatLog.innerHTML += `<div class="bot-message">${data.response}</div>`;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            chatLog.innerHTML += `<div class="bot-message">Error: ${error.message}</div>`;
        });

    });
    document.getElementById('chatbot-form').addEventListener('submit', function (e) {
        e.preventDefault();
        const userInput = document.getElementById('chatbot-input').value;
        const chatLog = document.getElementById('chat-log');
    
        chatLog.innerHTML += `<div class="user-message">${userInput}</div>`;
    
        document.getElementById('chatbot-input').value = '';
    
        chatLog.scrollTop = chatLog.scrollHeight;
    
        setTimeout(() => {
            chatLog.innerHTML += `<div class="bot-message">Thank you for your message. How can I assist you further?</div>`;
            chatLog.scrollTop = chatLog.scrollHeight;
        }, 1000);
    });
  });
