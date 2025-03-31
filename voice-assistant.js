/**
 * Voice Assistant for Intelligence Explorer
 * Provides voice interaction capabilities for blind users
 */

class VoiceAssistant {
    constructor() {
        this.recognition = null;
        this.synthesis = window.speechSynthesis;
        this.isListening = false;
        this.currentQuestion = null;
        this.currentQuestionNumber = 0;
        this.maxQuestions = 10;
        this.conversationHistory = [];
        this.userInfo = {
            name: '',
            age: '',
            background: ''
        };
        
        this.setupSpeechRecognition();
    }
    
    setupSpeechRecognition() {
        // Check if browser supports SpeechRecognition
        if ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();
            this.recognition.continuous = false;
            this.recognition.interimResults = false;
            this.recognition.lang = 'en-US';
            
            this.recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                this.handleSpeechInput(transcript);
            };
            
            this.recognition.onerror = (event) => {
                this.updateStatus('Error occurred in recognition: ' + event.error, 'error');
            };
            
            this.recognition.onend = () => {
                this.isListening = false;
                document.getElementById('listenBtn').innerHTML = '<i class="bi bi-mic-fill"></i> Listen';
                this.updateStatus('Voice recognition stopped', 'info');
            };
            
            // Set up listen button
            document.getElementById('listenBtn').addEventListener('click', () => {
                this.toggleListening();
            });
            
            this.updateStatus('Voice recognition ready', 'success');
        } else {
            this.updateStatus('Speech recognition not supported in this browser', 'error');
        }
    }
    
    startAssessment() {
        this.speak('Welcome to the Voice Intelligence Assessment. I\'ll guide you through a series of questions to determine your intelligence profile. Let\'s start with some basic information.');
        setTimeout(() => {
            this.askForUserInfo();
        }, 1000);
    }
    
    askForUserInfo() {
        // First collect basic user info
        if (!this.userInfo.name) {
            this.currentQuestion = {
                question: 'What is your name?',
                type: 'user_info',
                field: 'name'
            };
            this.ask('What is your name?');
        } else if (!this.userInfo.age) {
            this.currentQuestion = {
                question: 'How old are you?',
                type: 'user_info',
                field: 'age'
            };
            this.ask('How old are you?');
        } else if (!this.userInfo.background) {
            this.currentQuestion = {
                question: 'Can you briefly tell me about your educational or professional background?',
                type: 'user_info',
                field: 'background'
            };
            this.ask('Can you briefly tell me about your educational or professional background?');
        } else {
            // Move to assessment questions
            this.startQuestions();
        }
    }
    
    startQuestions() {
        this.currentQuestionNumber = 1;
        this.speak('Thank you for that information. Now, I\'ll ask you a series of questions to assess your intelligence profile. There will be ' + this.maxQuestions + ' questions in total.');
        setTimeout(() => {
            this.fetchNextQuestion();
        }, 1000);
    }
    
    fetchNextQuestion() {
        if (this.currentQuestionNumber > this.maxQuestions) {
            this.finishAssessment();
            return;
        }
        
        // In a real implementation, this would fetch from the backend
        // For demo purposes, we're using sample questions
        const sampleQuestions = [
            "Do you enjoy solving puzzles or brain teasers in your free time?",
            "How often do you find yourself creating music or responding emotionally to melodies?",
            "Would you say you're good at reading maps and navigating new places?",
            "How comfortable are you with public speaking or writing stories?",
            "Do you prefer team activities or solo pursuits?",
            "How often do you reflect on your own thoughts and feelings?",
            "Are you drawn to nature and do you notice patterns in the natural world?",
            "Do you find yourself thinking about philosophical questions about life and existence?",
            "How do you approach learning a new physical skill like dancing or sports?",
            "When solving a problem, do you prefer to use logic or intuition?"
        ];
        
        const question = sampleQuestions[this.currentQuestionNumber - 1];
        this.currentQuestion = {
            question: question,
            type: 'assessment',
            questionNumber: this.currentQuestionNumber
        };
        
        this.ask(`Question ${this.currentQuestionNumber} of ${this.maxQuestions}: ${question}`);
    }
    
    ask(question) {
        document.getElementById('voiceQuestion').textContent = question;
        this.speak(question);
        setTimeout(() => {
            this.updateStatus('Listening for your answer...', 'info');
            this.startListening();
        }, 1000);
    }
    
    handleSpeechInput(transcript) {
        document.getElementById('voiceTranscript').textContent = transcript;
        this.updateStatus('Processing your answer...', 'info');
        
        if (this.currentQuestion.type === 'user_info') {
            this.userInfo[this.currentQuestion.field] = transcript;
            this.speak('Thank you.');
            setTimeout(() => {
                this.askForUserInfo();
            }, 1000);
        } else if (this.currentQuestion.type === 'assessment') {
            // Save answer to conversation history
            this.conversationHistory.push({
                question: this.currentQuestion.question,
                answer: transcript,
                questionNumber: this.currentQuestion.questionNumber
            });
            
            this.speak('Thank you for your answer.');
            setTimeout(() => {
                this.currentQuestionNumber++;
                this.fetchNextQuestion();
            }, 1000);
        }
    }
    
    finishAssessment() {
        this.speak('Thank you for completing the assessment. I\'m analyzing your answers to generate your intelligence profile.');
        this.updateStatus('Generating results...', 'info');
        
        // In a real implementation, this would send data to the backend for analysis
        // For demo purposes, we're simulating a result
        setTimeout(() => {
            const demoResult = `
            Based on your responses, your primary intelligence type appears to be Linguistic Intelligence.
            
            Intelligence Profile:
            - Linguistic: 35.5%
            - Intrapersonal: 22.3% 
            - Logical-Mathematical: 18.2%
            - Interpersonal: 14.0%
            - Musical: 10.0%
            
            Your linguistic intelligence shows in your thoughtful responses and ability to express complex ideas. 
            You also demonstrate strong intrapersonal intelligence through your self-awareness.
            
            These strengths suggest you might excel in fields such as writing, teaching, psychology, or research.
            `;
            
            document.getElementById('voiceStatus').className = 'alert alert-success';
            document.getElementById('voiceStatus').innerHTML = '<h4>Your Results</h4><pre>' + demoResult + '</pre>';
            this.speak('I\'ve completed analyzing your responses. ' + demoResult.replace(/\n/g, ' '));
        }, 3000);
    }
    
    startListening() {
        if (this.recognition) {
            try {
                this.recognition.start();
                this.isListening = true;
                document.getElementById('listenBtn').innerHTML = '<i class="bi bi-stop-fill"></i> Stop Listening';
            } catch (e) {
                console.error('Error starting recognition:', e);
            }
        }
    }
    
    stopListening() {
        if (this.recognition && this.isListening) {
            this.recognition.stop();
            this.isListening = false;
        }
    }
    
    toggleListening() {
        if (this.isListening) {
            this.stopListening();
        } else {
            this.startListening();
        }
    }
    
    speak(text) {
        if (this.synthesis) {
            // Cancel any ongoing speech
            this.synthesis.cancel();
            
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.rate = 1.0;
            utterance.pitch = 1.0;
            this.synthesis.speak(utterance);
        }
    }
    
    updateStatus(message, type = 'info') {
        const statusElement = document.getElementById('voiceStatus');
        statusElement.textContent = message;
        
        // Update class based on message type
        statusElement.className = 'alert alert-' + type;
    }
}

// Initialize voice assistant when the page loads
document.addEventListener('DOMContentLoaded', function() {
    window.voiceAssistant = new VoiceAssistant();
});