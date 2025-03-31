// Accessibility Enhancement for Intelligence Explorer
// This script adds screen reading and voice input capabilities for blind users

class AccessibilityEnhancer {
    constructor() {
      this.synth = window.speechSynthesis;
      this.recognition = null;
      this.isListening = false;
      this.currentForm = null;
      this.currentQuestion = null;
      this.setupSpeechRecognition();
      this.setupAccessibilityButton();
      this.setupKeyboardShortcuts();
    }
  
    setupSpeechRecognition() {
      if ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        this.recognition = new SpeechRecognition();
        this.recognition.continuous = false;
        this.recognition.interimResults = false;
        this.recognition.lang = 'en-US';
  
        this.recognition.onresult = (event) => {
          const transcript = event.results[0][0].transcript;
          console.log('Recognized speech:', transcript);
          this.handleSpeechInput(transcript);
        };
  
        this.recognition.onerror = (event) => {
          console.error('Speech recognition error:', event.error);
          this.speak('Sorry, I couldn\'t understand. Please try again.');
        };
  
        this.recognition.onend = () => {
          this.isListening = false;
          if (this.shouldContinueListening) {
            this.shouldContinueListening = false;
            setTimeout(() => this.startListening(), 1000);
          }
        };
      } else {
        console.error('Speech Recognition API not supported by this browser');
      }
    }
  
    setupAccessibilityButton() {
      // Create floating accessibility button
      const button = document.createElement('button');
      button.textContent = 'Accessibility Mode';
      button.setAttribute('aria-label', 'Enable screen reader and voice input');
      button.style.position = 'fixed';
      button.style.bottom = '20px';
      button.style.right = '20px';
      button.style.zIndex = '9999';
      button.style.padding = '15px';
      button.style.backgroundColor = '#6a11cb';
      button.style.color = 'white';
      button.style.border = 'none';
      button.style.borderRadius = '10px';
      button.style.fontWeight = 'bold';
      button.style.boxShadow = '0 4px 8px rgba(0,0,0,0.2)';
      
      button.addEventListener('click', () => this.activateAccessibilityMode());
      
      document.body.appendChild(button);
      
      // Announce the availability of accessibility mode when page loads
      window.addEventListener('load', () => {
        setTimeout(() => {
          this.speak('Accessibility mode available. Press the button at the bottom right of the screen or press Alt+A to activate.');
        }, 1000);
      });
    }
    
    setupKeyboardShortcuts() {
      document.addEventListener('keydown', (event) => {
        // Alt+A to activate accessibility mode
        if (event.altKey && event.key === 'a') {
          this.activateAccessibilityMode();
        }
      });
    }
  
    activateAccessibilityMode() {
      this.speak('Accessibility mode activated. I will now read the page content to you.');
      
      // Identify current page and read appropriate content
      setTimeout(() => {
        if (window.location.pathname === '/' || window.location.pathname.includes('index')) {
          this.handleHomePage();
        } else if (window.location.pathname.includes('setup')) {
          this.handleSetupPage();
        } else if (window.location.pathname.includes('chat')) {
          this.handleChatPage();
        } else if (window.location.pathname.includes('result')) {
          this.handleResultPage();
        }
      }, 1500);
    }
  
    handleHomePage() {
      const introText = 'Welcome to Intelligence Explorer. This application helps you discover your unique intelligence profile based on Howard Gardner\'s Multiple Intelligences Theory.';
      const instructionsText = 'To begin your intelligence assessment, say "start" or "begin" after I finish speaking.';
      
      this.speak(`${introText} ${instructionsText}`, () => {
        this.listenFor(['start', 'begin'], () => {
          window.location.href = document.querySelector('a[href*="setup"]').href;
        });
      });
    }
  
    handleSetupPage() {
      this.currentForm = document.querySelector('form');
      
      if (!this.currentForm) {
        this.speak('Error: Setup form not found. Please refresh the page and try again.');
        return;
      }
      
      const setupIntro = 'Let\'s set up your profile. I\'ll ask for some information before we begin the assessment.';
      
      this.speak(setupIntro, () => {
        // Process each form field in sequence
        const formFields = Array.from(this.currentForm.querySelectorAll('input, select, textarea'))
          .filter(el => el.type !== 'submit');
        
        this.processFormFieldsSequentially(formFields, 0, () => {
          this.speak('Thank you. Say "submit" when you\'re ready to continue to the questions.', () => {
            this.listenFor(['submit', 'continue', 'next'], () => {
              this.submitForm(this.currentForm);
            });
          });
        });
      });
    }
  
    processFormFieldsSequentially(fields, index, onComplete) {
      if (index >= fields.length) {
        onComplete();
        return;
      }
      
      const field = fields[index];
      let fieldDescription = '';
      
      // Get the label for this field
      const labelElement = document.querySelector(`label[for="${field.id}"]`);
      if (labelElement) {
        fieldDescription = labelElement.textContent;
      } else {
        // Try to get placeholder or name if label not found
        fieldDescription = field.placeholder || field.name || `Field ${index + 1}`;
      }
      
      this.speak(`Please provide your ${fieldDescription}`, () => {
        this.listenForInput((input) => {
          if (field.tagName.toLowerCase() === 'select') {
            // Handle dropdown selection
            this.setSelectValue(field, input);
          } else {
            field.value = input;
          }
          
          this.speak(`You said: ${input}. Is this correct? Say yes to confirm or no to try again.`, () => {
            this.listenFor(['yes', 'correct', 'that\'s right'], () => {
              // Move to the next field
              this.processFormFieldsSequentially(fields, index + 1, onComplete);
            }, ['no', 'incorrect', 'wrong'], () => {
              // Retry the current field
              this.processFormFieldsSequentially(fields, index, onComplete);
            });
          });
        });
      });
    }
  
    setSelectValue(selectElement, spokenValue) {
      // Convert spoken value to lowercase for comparison
      const spokenValueLower = spokenValue.toLowerCase();
      
      // Try to find an option that matches the spoken value
      let matchFound = false;
      
      for (const option of selectElement.options) {
        if (option.text.toLowerCase() === spokenValueLower || 
            option.value.toLowerCase() === spokenValueLower) {
          selectElement.value = option.value;
          matchFound = true;
          break;
        }
      }
      
      if (!matchFound) {
        // Try partial matching
        for (const option of selectElement.options) {
          if (option.text.toLowerCase().includes(spokenValueLower) || 
              option.value.toLowerCase().includes(spokenValueLower)) {
            selectElement.value = option.value;
            matchFound = true;
            break;
          }
        }
      }
      
      return matchFound;
    }
  
    handleChatPage() {
      const questionElement = document.querySelector('.question') || document.querySelector('h2') || document.querySelector('p');
      
      if (!questionElement) {
        this.speak('Error: Question not found. Please refresh the page and try again.');
        return;
      }
      
      this.currentQuestion = questionElement.textContent;
      const questionCountText = document.querySelector('.question-count')?.textContent || '';
      
      this.speak(`${questionCountText} ${this.currentQuestion}`, () => {
        this.speak('Please provide your answer.', () => {
          this.listenForInput((answer) => {
            const answerField = document.querySelector('textarea') || document.querySelector('input[type="text"]');
            
            if (answerField) {
              answerField.value = answer;
              
              this.speak(`Your answer is: ${answer}. Is this correct? Say yes to submit or no to try again.`, () => {
                this.listenFor(['yes', 'correct', 'that\'s right'], () => {
                  const form = document.querySelector('form');
                  if (form) {
                    this.submitForm(form);
                  } else {
                    this.speak('Error: Form not found. Please refresh the page and try again.');
                  }
                }, ['no', 'incorrect', 'wrong'], () => {
                  // Retry getting the answer
                  this.handleChatPage();
                });
              });
            } else {
              this.speak('Error: Answer field not found. Please refresh the page and try again.');
            }
          });
        });
      });
    }
  
    handleResultPage() {
      const resultElement = document.querySelector('.result-container') || document.querySelector('.card-body');
      
      if (!resultElement) {
        this.speak('Error: Results not found. Please refresh the page and try again.');
        return;
      }
      
      const resultText = resultElement.textContent.replace(/\s+/g, ' ').trim();
      
      this.speak('Here are your results: ' + resultText, () => {
        this.speak('Would you like me to repeat the results? Say yes to repeat or no to end.', () => {
          this.listenFor(['yes', 'repeat', 'again'], () => {
            this.handleResultPage();
          }, ['no', 'end', 'finish'], () => {
            this.speak('Thank you for using Intelligence Explorer. Goodbye!');
          });
        });
      });
    }
  
    speak(text, onComplete) {
      if (this.synth.speaking) {
        console.log('Speech already in progress');
        this.synth.cancel();
      }
      
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 0.9; // Slightly slower for better comprehension
      
      if (onComplete) {
        utterance.onend = onComplete;
      }
      
      this.synth.speak(utterance);
    }
  
    startListening() {
      if (!this.recognition) {
        console.error('Speech recognition not supported or not initialized');
        return;
      }
      
      try {
        this.recognition.start();
        this.isListening = true;
        console.log('Listening started');
      } catch (error) {
        console.error('Error starting recognition:', error);
      }
    }
  
    listenFor(acceptTerms, onAccept, rejectTerms = [], onReject = null) {
      this.startListening();
      
      const originalOnResult = this.recognition.onresult;
      
      this.recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript.toLowerCase();
        console.log('Heard:', transcript);
        
        // Check for accept terms
        const isAccepted = acceptTerms.some(term => transcript.includes(term.toLowerCase()));
        
        // Check for reject terms if provided
        const isRejected = rejectTerms.length > 0 && 
                           rejectTerms.some(term => transcript.includes(term.toLowerCase()));
        
        if (isAccepted) {
          // Restore original handler
          this.recognition.onresult = originalOnResult;
          onAccept();
        } else if (isRejected && onReject) {
          // Restore original handler
          this.recognition.onresult = originalOnResult;
          onReject();
        } else {
          // Not recognized, try again
          this.speak('Sorry, I didn\'t understand. Please try again.', () => {
            this.shouldContinueListening = true;
          });
        }
      };
    }
  
    listenForInput(callback) {
      this.startListening();
      
      const originalOnResult = this.recognition.onresult;
      
      this.recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        // Restore original handler
        this.recognition.onresult = originalOnResult;
        callback(transcript);
      };
    }
  
    submitForm(form) {
      if (!form) return;
      
      const submitButton = form.querySelector('input[type="submit"]') || 
                           form.querySelector('button[type="submit"]') ||
                           form.querySelector('button');
      
      if (submitButton) {
        this.speak('Submitting your information...', () => {
          submitButton.click();
        });
      } else {
        // If no submit button found, try to submit form directly
        this.speak('Submitting your information...', () => {
          form.submit();
        });
      }
    }
  
    handleSpeechInput(transcript) {
      console.log('Processing speech input:', transcript);
      // This method can be extended for more complex speech command handling
    }
  }
  
  // Initialize the accessibility enhancer when page is loaded
  document.addEventListener('DOMContentLoaded', () => {
    window.accessibilityEnhancer = new AccessibilityEnhancer();
  });