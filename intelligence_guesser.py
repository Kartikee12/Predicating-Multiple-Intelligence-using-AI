import os
import json
import PyPDF2
import numpy as np
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
from dotenv import load_dotenv

class IntelligenceGuesser:
    def __init__(self, docs_folder=r'docs', embedding_model='all-MiniLM-L6-v2'):
        """
        Initialize the Intelligence Guesser with document embeddings and Gemini LLM
        
        :param docs_folder: Folder containing PDF documents
        :param embedding_model: Sentence Transformer model for embeddings
        """
        # Load environment variables for API key
        load_dotenv()
        
        # Set up Gemini API
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        
        self.docs_folder = docs_folder
        self.embedding_model = SentenceTransformer(embedding_model)
        
        # Configure Gemini model
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
        # State tracking
        self.current_context = {}
        self.knowledge_base = {}
        self.conversation_history = []
        
        
        # Document embedding processing
        self.process_documents()
    
    def process_documents(self):
        """
        Scan PDF documents, extract text, and create embeddings
        """
        self.knowledge_base = {}
        
        for filename in os.listdir(self.docs_folder):
            if filename.endswith('.pdf'):
                filepath = os.path.join(self.docs_folder, filename)
                with open(filepath, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    full_text = ''
                    for page in pdf_reader.pages:
                        full_text += page.extract_text() + '\n'
                    
                    # Create embedding for the document
                    embedding = self.embedding_model.encode([full_text])[0]
                    
                    self.knowledge_base[filename] = {
                        'text': full_text,
                        'embedding': embedding
                    }
        
        print(f"Processed {len(self.knowledge_base)} documents")
    
    def generate_question(self, context=None):
        """
        Generate an intelligent question using Google's Gemini model
        
        :param context: Additional context for question generation
        :return: Generated question dictionary
        """
        sample_data = """Multiple Intelligences Test - based on Howard Gardner's MI Model
        (manual version - see businessballs.com for self-calculating version)
        Score or tick the statements in the white-out boxes only

        I like to learn more about myself 1
        I can play a musical instrument 2
        I find it easiest to solve problems when I am doing something physical 3
        I often have a song or piece of music in my head 4
        I find budgeting and managing my money easy 5
        I find it easy to make up stories 6
        I have always been physically well co-ordinated 7
        When talking to someone, I tend to listen to the words they use not just what they mean 8
        I enjoy crosswords, word searches or other word puzzles 9
        I don’t like ambiguity, I like things to be clear 10
        I enjoy logic puzzles such as 'sudoku' 11
        I like to meditate 12
        Music is very important to me 13
        I am a convincing liar (if I want to be) 14

        more info at businessballs.com

        Score the statements: 1 = Mostly Disagree, 2 = Slightly Disagree, 3 = Slightly Agree, 4 = Mostly Agree
        Alternatively for speed, and if easier for young people - tick the box if the statement is more true for you than not.
        Adults over 16 complete all questions. Young people between 8-16 answer red questions only.
        This is page 1 of 4.

        I play a sport or dance 15
        I am very interested in psychometrics (personality testing) and IQ tests 16
        People behaving irrationally annoy me 17
        I find that the music that appeals to me is often based on how I feel emotionally 18
        I am a very social person and like being with other people 19
        I like to be systematic and thorough 20
        I find graphs and charts easy to understand 21
        I can throw things well - darts, skimming pebbles, frisbees, etc 22
        I find it easy to remember quotes or phrases 23
        I can always recognise places that I have been before, even when I was very young 24
        I enjoy a wide variety of musical styles 25
        When I am concentrating I tend to doodle 26
        I could manipulate people if I choose to 27
        I can predict my feelings and behaviours in certain situations fairly accurately 28
        I find mental arithmetic easy 29
        I can identify most sounds without seeing what causes them 30
        At school one of my favourite subjects is / was English 31
        I like to think through a problem carefully, considering all the consequences 32
        I enjoy debates and discussions 33
        I love adrenaline sports and scary rides 34
        I enjoy individual sports best 35
        I care about how those around me feel 36
        My house is full of pictures and photographs 37
        I enjoy and am good at making things - I'm good with my hands 38
        I like having music on in the background 39
        I find it easy to remember telephone numbers 40

        I set myself goals and plans for the future 41
        I am a very tactile person 42
        I can tell easily whether someone likes me or dislikes me 43
        I can easily imagine how an object would look from another perspective 44
        I never use instructions for flat-pack furniture 45
        I find it easy to talk to new people 46
        To learn something new, I need to just get on and try it 47
        I often see clear images when I close my eyes 48
        I don’t use my fingers when I count 49
        I often talk to myself – out loud or in my head 50
        At school I loved / love music lessons 51
        When I am abroad, I find it easy to pick up the basics of another language 52
        I find ball games easy and enjoyable 53
        My favourite subject at school is / was maths 54
        I always know how I am feeling 55
        I am realistic about my strengths and weaknesses 56
        I keep a diary 57
        I am very aware of other people’s body language 58
        My favourite subject at school was / is art 59
        I find pleasure in reading 60
        I can read a map easily 61
        It upsets me to see someone cry and not be able to help 62
        I am good at solving disputes between others 63
        I have always dreamed of being a musician or singer 64
        I prefer team sports 65
        Singing makes me feel happy 66

        I never get lost when I am on my own in a new place 67
        If I am learning how to do something, I like to see drawings and diagrams of how it works 68
        I am happy spending time alone ... (text truncated for brevity)"""
        
        intelligence_data = """The Seven Multiple Intelligences in Children  
            Children who are strongly:  Think  Love  Need  
            Linguistic: in words – reading, writing, telling stories, playing word games, etc.
                    (e.g., books, tapes, writing tools, paper diaries, dialogues, discussions, debates, stories)
            Logical-Mathematical: by reasoning, experimenting, questioning, figuring out puzzles, calculating, etc.
                    (e.g., things to explore and think about, science materials, manipulatives, trips to the planetarium and science museum)
            Spatial: in images and pictures – designing, drawing, visualizing, doodling, etc.
                    (e.g., art, LEGOs, videos, movies, slides, imagination games, mazes, puzzles, illustrated books, trips to art museums)
            Bodily-Kinesthetic: through somatic sensations – dancing, running, jumping, building, touching, gesturing, etc.
                    (e.g., role play, drama, movement, things to build, sports and physical games, tactile experiences, hands-on learning)
            Musical: via rhythms and melodies – singing, whistling, humming, tapping feet and hands, listening, etc.
                    (e.g., sing-along time, trips to concerts, music playing at home and school, musical instruments)
            Interpersonal: by bouncing ideas off other people – leading, organizing, relating, manipulating, mediating, partying, etc.
                    (e.g., friends, group games, social gatherings, community events, clubs, mentors/apprenticeships)
            Intrapersonal: deeply inside themselves – setting goals, meditating, dreaming, being quiet,
                    (e.g., secret places, time alone, self-paced projects, choices)
            """
        # Prepare prompt for question generation
        prompt = f"""Consider Yourself a Pyschologist who is expert in human intelligence and brain development.
        Generate an insightful question that can help assess human intelligence. 
        Consider age,background and harward gardners theory to generate question.
        ASK SIMPLE QUESTIONS , LIKE DONE IN HARWARD THEORY:
        EXMAPLE :
        Multiple Intelligences Test Example Data:
        {sample_data}
        Intelligence data : {intelligence_data}
        Consider the following contexts:
        - Previous conversation context: {context or 'None'}
        - Available document knowledge: {', '.join(self.knowledge_base.keys())}

        Generate a question with the following requirements:
        1. ASK SIMPLE QUESTIONS , LIKE DONE IN HARWARD THEORY
        2.TRY TO ASK NEW QUESTION RELATED TO PREVIOUS QUESTIONS BUT ASK OF DIFFERENT Intelligence data TYPE
        3. It can be either multiple-choice or open-ended
        4. Include a rationale for how this question reveals intelligence
        5. Refer Multiple Intelligences Test Example Data
        6.Start the question by referring previous questions answers
        7.BE FRIENDLY AND ASK QUESTION IN NON-PROFESSIONAL TONE
        
        Provide the response in this exact JSON format:
        {{
            "question": "...",
            "type": "mcq" or "textual",
            "options": ["Option 1", "Option 2", ...] or null,
            "intelligence_indicators": ["analytical", "creative", "logical", ...],
            "rationale": "Why this question helps assess intelligence"
        }}

        IMPORTANT: Ensure the JSON is valid and directly parseable. Do not include any markdown code blocks or additional text.
        """
        
        try:
            # Generate response
            response = self.model.generate_content(prompt)
            
            # Try to parse the JSON response
            try:
                question_data = json.loads(response.text)
            except json.JSONDecodeError:
                # Fallback parsing if JSON is not clean
                # Extract JSON-like content between { and }
                import re
                json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
                if json_match:
                    question_data = json.loads(json_match.group(0))
                else:
                    raise ValueError("Could not parse JSON")
            
            return question_data
        
        except Exception as e:
            print(f"Error generating question: {e}")
            # Fallback question if generation fails
            return {
                "question": "What problem-solving approach do you typically use?",
                "type": "textual",
                "options": None,
                "intelligence_indicators": ["analytical", "strategic"],
                "rationale": "Assesses methodical thinking and problem-solving skills"
            }
    
    def start_conversation(self):
        """
        Initiate conversation and gather user information
        """
        print("Welcome to the Gemini-Powered Intelligence Guesser!")
        
        # User information gathering
        self.current_context['user_info'] = {
            'name': input("What is your name? "),
            'age': input("How old are you? "),
            'background': input("What is your educational/professional background? ")
        }
        
        # Question preference
        question_type = input("Would you prefer Multiple Choice (MCQ) or Textual questions? (mcq/textual): ").lower()
        self.current_context['question_preference'] = question_type
        
        print(f"\nThank you, {self.current_context['user_info']['name']}! Let's begin our intelligence assessment.")
        self.run_assessment()
    
    def run_assessment(self, max_questions=5):
        """
        Run the intelligence assessment process with dynamically generated questions
        
        :param max_questions: Maximum number of questions to ask
        """
        intelligence_indicators = {}
        
        for _ in range(max_questions):
            # Generate a question based on current context
            question_data = self.generate_question(
                context=json.dumps(self.conversation_history[-3:] if self.conversation_history else None)
            )
            
            # Filter questions based on user preference
            if (self.current_context['question_preference'] == 'mcq' and question_data.get('type') == 'mcq') or \
               (self.current_context['question_preference'] == 'textual' and question_data.get('type') == 'textual'):
                
                # Ask question
                print(f"\n{question_data['question']}")
                
                if question_data['type'] == 'mcq':
                    for i, option in enumerate(question_data.get('options', []), 1):
                        print(f"{i}. {option}")
                    
                    # Get user input with validation
                    while True:
                        try:
                            user_choice = int(input("Enter the number of your choice: "))
                            if 1 <= user_choice <= len(question_data.get('options', [])):
                                user_answer = question_data['options'][user_choice - 1]
                                break
                            else:
                                print("Invalid choice. Please try again.")
                        except ValueError:
                            print("Please enter a valid number.")
                
                else:  # Textual question
                    user_answer = input("Your response: ")
                
                # Store conversation history
                self.conversation_history.append({
                    'question': question_data['question'],
                    'answer': user_answer,
                    'intelligence_indicators': question_data.get('intelligence_indicators', [])
                })
                
                # Update intelligence indicators
                for indicator in question_data.get('intelligence_indicators', []):
                    intelligence_indicators[indicator] = intelligence_indicators.get(indicator, 0) + 1
        
        # Analyze results
        self.analyze_results(intelligence_indicators)
    
    def analyze_results(self, intelligence_indicators):
        """
        Analyze intelligence assessment results
        
        :param intelligence_indicators: Dictionary of intelligence indicators
        """
        # Determine primary intelligence type
        if intelligence_indicators:
            primary_intelligence = max(intelligence_indicators, key=intelligence_indicators.get)
            confidence_score = intelligence_indicators[primary_intelligence] / sum(intelligence_indicators.values())
            
            print("\n--- Intelligence Assessment Results ---")
            print(f"Primary Intelligence Type: {primary_intelligence}")
            print(f"Confidence Score: {confidence_score:.2%}")
            print("\nRationale:")
            print("This assessment provides insights into your cognitive strengths based on dynamically generated questions.")
        else:
            print("Insufficient data to determine intelligence type.")
            
    def retrieve_context(self, query, n_results=5):
        """
        Retrieve relevant context from knowledge base using similarity search
        
        :param query: Query text to search for
        :param n_results: Number of results to return
        :return: String containing relevant context
        """
        # Convert query to embedding
        query_embedding = self.embedding_model.encode([query])[0]
        
        # Calculate similarity scores with all documents
        similarity_scores = {}
        for doc_name, doc_data in self.knowledge_base.items():
            # Calculate cosine similarity
            similarity = np.dot(query_embedding, doc_data['embedding']) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(doc_data['embedding'])
            )
            similarity_scores[doc_name] = similarity
        
        # Get top n_results documents
        top_docs = sorted(similarity_scores.items(), key=lambda x: x[1], reverse=True)[:n_results]
        
        # Extract and concatenate relevant text from top documents
        context_text = ""
        for doc_name, _ in top_docs:
            # Add document name and excerpt of content
            context_text += f"From {doc_name}:\n"
            # Get first 500 characters of document as preview
            doc_preview = self.knowledge_base[doc_name]['text'][:500] + "..."
            context_text += doc_preview + "\n\n"
        
        return context_text
    def generate_detailed_analysis(self, conversation_history):
        """
        Generate a detailed analysis of the user's intelligence profile based on
        their conversation history.
        """
        # Convert the conversation history to a format suitable for context retrieval
        conversation_summary = ""
        for i, entry in enumerate(conversation_history):
            conversation_summary += f"Question {i+1}: {entry['question']}\n"
            conversation_summary += f"Answer: {entry['answer']}\n"
            conversation_summary += f"Intelligence Indicators: {', '.join(entry['intelligence_indicators'])}\n\n"
        
        # Retrieve relevant context from the Gardner document
        context = self.retrieve_context(
            query=f"Gardner's theory detailed explanation of intelligence types and interpretation",
            n_results=5
        )
        
        # Generate the analysis
        prompt = f"""
        Based on Howard Gardner's Theory of Multiple Intelligences, analyze this user's intelligence profile.
        
        Conversation History:
        {conversation_summary}
        
        Context Information on Gardner's Theory:
        {context}
        
        Please provide:
        1. An assessment of their primary and secondary intelligence types
        2. Specific strengths indicated by their answers
        3. Potential career or learning paths that align with their intelligence profile
        4. Suggestions for developing their predominant intelligences further
        5. How their intelligences might complement each other
        
        Make the analysis warm, encouraging, and personalized, as if coming from a knowledgeable psychologist.
        """
        
        response = self.model.generate_content(prompt)
        return response.text

def main():
    # Ensure you have a .env file with GEMINI_API_KEY
    intelligence_guesser = IntelligenceGuesser()
    intelligence_guesser.start_conversation()

if __name__ == "__main__":
    main()