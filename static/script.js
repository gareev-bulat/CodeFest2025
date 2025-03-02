// document.addEventListener('DOMContentLoaded', function () {
//   const healthForm = document.getElementById('healthForm');
//   const predictionText = document.getElementById('predictionText');
//   const suggestionsContainer = document.getElementById('suggestionsContainer');
//   const spinner = document.getElementById('loadingSpinner');
//   const chatLog = document.getElementById('chat-log');
//   const chatbotForm = document.getElementById('chatbot-form');
//   const chatbotInput = document.getElementById('chatbot-input');

//   // Handle health form submission
//   healthForm.addEventListener('submit', function (e) {
//       e.preventDefault();
//       // Show the spinner
//       spinner.style.display = 'block';
//       const formData = new FormData(healthForm);
//       const data = {};
//       formData.forEach((value, key) => {
//           data[key] = value;
//       });

//       fetch('/predict', {
//           method: 'POST',
//           headers: { 'Content-Type': 'application/json' },
//           body: JSON.stringify(data)
//       })
//       .then(response => response.json())
//       .then(data => {
//           if(data.error){
//               predictionText.innerHTML = `<p>Error: ${data.error}</p>`;
//               suggestionsContainer.innerHTML = "";
//           } else {
//               predictionText.innerHTML = `<strong>Prediction:</strong> ${data.prediction === 1 ? 'High Risk of Diabetes' : 'Low Risk of Diabetes'}`;
//               suggestionsContainer.innerHTML = `<h3>Health Suggestions:</h3>${data.suggestions}`;
//               // Optionally, append suggestions to the chatbot log as well
//               chatLog.innerHTML += `<div class="bot-message">${data.suggestions}</div>`;
//           }
//       })
//       .catch(error => {
//           console.error('Error:', error);
//           predictionText.innerHTML = `<p>Error: ${error}</p>`;
//       })
//       .finally(() => {
//           // Hide the spinner after data loads or error occurs
//           spinner.style.display = 'none';
//       });
//   });

//   // Handle chatbot form submission (if needed)
//   chatbotForm.addEventListener('submit', function (e) {
//       e.preventDefault();
//       const userMessage = chatbotInput.value.trim();
//       if (!userMessage) return;
//       chatLog.innerHTML += `<div class="user-message">${userMessage}</div>`;
//       chatbotInput.value = '';
//       // OPTIONAL: Implement fetch call for additional chatbot responses if needed.
//   });
// });
document.addEventListener('DOMContentLoaded', function () {
    const healthForm = document.getElementById('healthForm');
    const predictionText = document.getElementById('predictionText');
    const suggestionsContainer = document.getElementById('suggestionsContainer');
    const spinner = document.getElementById('loadingSpinner');
    const chatLog = document.getElementById('chat-log');
    const chatbotForm = document.getElementById('chatbot-form');
    const chatbotInput = document.getElementById('chatbot-input');
  
    let predictionResult = null; // Store the prediction result for chatbot interaction
  
    // Handle health form submission
    healthForm.addEventListener('submit', function (e) {
        e.preventDefault();
        // Show the spinner
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
            if(data.error){
                predictionText.innerHTML = `<p>Error: ${data.error}</p>`;
                suggestionsContainer.innerHTML = "";
            } else {
                predictionText.innerHTML = `<strong>Prediction:</strong> ${data.prediction === 1 ? 'High Risk of Diabetes' : 'Low Risk of Diabetes'}`;
                suggestionsContainer.innerHTML = `<h3>Health Suggestions:</h3>${data.suggestions}`;
                // Store the prediction result for chatbot interaction
                predictionResult = data.prediction;
                // Show the chatbot interface
                document.getElementById('chatbot').style.display = 'block';
                // Append suggestions to the chatbot log
                chatLog.innerHTML += `<div class="bot-message">${data.suggestions}</div>`;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            predictionText.innerHTML = `<p>Error: ${error}</p>`;
        })
        .finally(() => {
            // Hide the spinner after data loads or error occurs
            spinner.style.display = 'none';
        });
    });
  
    // Handle chatbot form submission
    chatbotForm.addEventListener('submit', function (e) {
        e.preventDefault();
        const userMessage = chatbotInput.value.trim();
        if (!userMessage) return;
  
        // Append the user's message to the chat log
        chatLog.innerHTML += `<div class="user-message">${userMessage}</div>`;
        chatbotInput.value = '';
  
        // Show a loading indicator in the chat log
        chatLog.innerHTML += `<div class="bot-message">Loading...</div>`;
  
        // Send the user's message and prediction result to the backend
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
            // Remove the loading indicator
            chatLog.querySelector('.bot-message:last-child').remove();
            // Append the chatbot's response to the chat log
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
  });
