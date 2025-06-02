document.addEventListener('DOMContentLoaded', () => {
    const questions = [
        "What happened during the incident?",
        "When did the incident happen?",
        "Where did the incident happen?"
    ];
    let currentQuestionIndex = 0;
    let answers = [];
    
    const questionElement = document.getElementById('question');
    const startButton = document.getElementById('startButton');
    const statusElement = document.getElementById('status');
    const transcriptionElement = document.getElementById('transcription');
    const resultsElement = document.getElementById('results');
    const restartButton = document.getElementById('restartButton');
    const textForm = document.getElementById('textForm');
    
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'en-US';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;
    
    let isListening = false;
    
    function setStatus(message) {
        statusElement.textContent = `Status: ${message}`;
    }
    
    function askQuestion() {
        if (currentQuestionIndex < questions.length) {
            const question = questions[currentQuestionIndex];
            questionElement.textContent = question;
            setStatus('Listening... Please speak your answer.');
            
            // Speak the question
            const utterance = new SpeechSynthesisUtterance(question);
            utterance.lang = 'en-US';
            window.speechSynthesis.speak(utterance);
            
            // Start listening
            recognition.start();
            isListening = true;
        } else {
            // Process answers
            processAnswers();
        }
    }
    
    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        transcriptionElement.textContent = `Transcribed: ${transcript}`;
        answers.push(transcript);
        currentQuestionIndex++;
        recognition.stop();
        isListening = false;
        
        setTimeout(askQuestion, 1000); // Delay before next question
    };
    
    recognition.onerror = (event) => {
        setStatus(`Error: ${event.error}`);
        recognition.stop();
        isListening = false;
        startButton.disabled = false;
    };
    
    recognition.onend = () => {
        if (isListening) {
            recognition.start();
        }
    };
    
    function processAnswers() {
        setStatus('Processing answers...');
        fetch('/process_answers', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ answers })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                setStatus(`Error: ${data.error}`);
            } else {
                setStatus('Success! Please note down your Reference ID and Password to track your report.');
                displayResults(data);
            }
        })
        .catch(error => {
            setStatus(`Error: ${error.message}`);
        });
    }
    
    function displayResults(data) {
        document.getElementById('category').textContent = data.category || 'Not mentioned';
        document.getElementById('date').textContent = data.date || 'Not mentioned';
        document.getElementById('time').textContent = data.time || 'Not mentioned';
        document.getElementById('accused').textContent = data.accused || 'Not mentioned';
        document.getElementById('location').textContent = data.location || 'Not mentioned';
        document.getElementById('summary').textContent = data.summary || 'Not mentioned';
        document.getElementById('reference_id').textContent = data.reference_id || 'Not available';
        document.getElementById('password').textContent = data.password || 'Not available';
        resultsElement.style.display = 'block';
        startButton.disabled = false;
    }
    
    startButton.addEventListener('click', () => {
        startButton.disabled = true;
        currentQuestionIndex = 0;
        answers = [];
        resultsElement.style.display = 'none';
        transcriptionElement.textContent = '';
        askQuestion();
    });
    
    restartButton.addEventListener('click', () => {
        currentQuestionIndex = 0;
        answers = [];
        resultsElement.style.display = 'none';
        transcriptionElement.textContent = '';
        questionElement.textContent = 'Press "Start Voice Agent" to begin.';
        setStatus('Waiting to start...');
        startButton.disabled = false;
    });
    
    textForm.addEventListener('submit', (event) => {
        event.preventDefault();
        const formData = new FormData(textForm);
        fetch('/submit_text', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                setStatus(`Error: ${data.error}`);
            } else {
                setStatus('Success! Please note down your Reference ID and Password to track your report.');
                displayResults(data);
            }
        })
        .catch(error => {
            setStatus(`Error: ${error.message}`);
        });
    });
});