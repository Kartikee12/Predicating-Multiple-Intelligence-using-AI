import os
import json
from flask import Flask, render_template, request, redirect, url_for, session
from intelligence_guesser import IntelligenceGuesser

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace with a secure key

# Instantiate your IntelligenceGuesser once (loads documents and embeddings)
ig = IntelligenceGuesser()

# Maximum number of questions to ask before showing results
MAX_QUESTIONS = 10

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Store user info and preferences in session and the intelligence guesser's context
        session['user_info'] = {
            'name': request.form.get('name'),
            'age': request.form.get('age'),
            'background': request.form.get('background')
        }
        session['question_preference'] = request.form.get('question_preference')
        session['conversation_history'] = []
        session['question_count'] = 0
        
        ig.current_context['user_info'] = session['user_info']
        ig.current_context['question_preference'] = session['question_preference']
        return redirect(url_for('chat'))
    return render_template('index.html')

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    confidence_threshold = 0.40

    if request.method == 'POST':
        user_answer = request.form.get('answer')
        current_question = session.get('current_question')
        
        # If the question is MCQ and the voice input is ambiguous, use Gemini to match the answer
        if current_question.get('type') == 'mcq':
            options = current_question.get('options', [])
            if user_answer not in options:
                # Prepare a prompt for Gemini to map the voice input to one of the options
                prompt = (
                    f"Given the following multiple choice question:\n\n"
                    f"Question: {current_question.get('question')}\n"
                    f"Options: {options}\n\n"
                    f"The voice response was: '{user_answer}'.\n"
                    "Which option does this answer best correspond to? "
                    "Reply with exactly one of the options."
                )
                try:
                    gemini_response = ig.model.generate_content(prompt)
                    mapped_answer = gemini_response.text.strip()
                    # Optionally validate that the returned answer is in options.
                    if mapped_answer in options:
                        user_answer = mapped_answer
                    else:
                        # Fallback: if Gemini answer is not one of the options, choose the closest match
                        user_answer = options[0]
                except Exception as e:
                    print("Gemini mapping failed:", e)
                    user_answer = options[0]  # fallback to first option
        # Continue with existing processing
        conversation_history = session.get('conversation_history', [])
        conversation_history.append({
            'question': current_question.get('question'),
            'answer': user_answer,
            'intelligence_indicators': current_question.get('intelligence_indicators', [])
        })
        session['conversation_history'] = conversation_history
        ig.conversation_history = conversation_history
        session['question_count'] = session.get('question_count', 0) + 1
        
        intelligence_indicators, highest_confidence = calculate_confidence(conversation_history)
        if highest_confidence >= confidence_threshold or session['question_count'] >= MAX_QUESTIONS:
            result = analyze_results_web(conversation_history)
            return render_template('result.html', result=result)

    if session.get('question_count', 0) >= MAX_QUESTIONS:
        result = analyze_results_web(session.get('conversation_history', []))
        return render_template('result.html', result=result)

    context = json.dumps(session.get('conversation_history', []))
    question_data = ig.generate_question(context=context)
    session['current_question'] = question_data

    question_count = session.get('question_count', 0) + 1
    return render_template('chat.html', question=question_data, question_count=question_count, max_questions=MAX_QUESTIONS)


def calculate_confidence(conversation_history):
    """Calculate confidence scores for each intelligence type"""
    intelligence_indicators = {}
    
    # Count occurrences of each intelligence indicator
    for entry in conversation_history:
        for indicator in entry.get('intelligence_indicators', []):
            intelligence_indicators[indicator] = intelligence_indicators.get(indicator, 0) + 1
    
    # Calculate highest confidence
    highest_confidence = 0
    if intelligence_indicators and sum(intelligence_indicators.values()) > 0:
        highest_confidence = max(intelligence_indicators.values()) / sum(intelligence_indicators.values())
        
    return intelligence_indicators, highest_confidence

def analyze_results_web(conversation_history):
    """Generate a comprehensive analysis of the user's intelligence profile"""
    # Aggregate intelligence indicators
    intelligence_indicators, confidence_score = calculate_confidence(conversation_history)
    
    if intelligence_indicators:
        # Get the primary intelligence type
        primary_intelligence = max(intelligence_indicators, key=intelligence_indicators.get)
        
        # Get all intelligences sorted by confidence
        sorted_intelligences = sorted(
            intelligence_indicators.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        # Calculate percentages for each intelligence type
        total_indicators = sum(intelligence_indicators.values())
        intelligence_percentages = {
            intel: (count / total_indicators * 100) 
            for intel, count in intelligence_indicators.items()
        }
        
        # Format detailed results
        result_text = (
            f"Primary Intelligence Type: {primary_intelligence}\n"
            f"Confidence Score: {confidence_score:.2%}\n\n"
            f"Questions Answered: {len(conversation_history)}\n\n"
            "Intelligence Profile:\n"
        )
        
        # Add each intelligence with its percentage
        for intel, count in sorted_intelligences:
            percentage = intelligence_percentages[intel]
            result_text += f"- {intel}: {percentage:.1f}%\n"
        
        # Ask the intelligence guesser to generate more detailed insights
        detailed_insights = ig.generate_detailed_analysis(conversation_history)
        result_text += f"\n\nDetailed Analysis:\n{detailed_insights}"
        
    else:
        result_text = "Insufficient data to determine intelligence type."
    
    return result_text

if __name__ == '__main__':
    app.run(debug=True)