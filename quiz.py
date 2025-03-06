from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import random

app = Flask(__name__)
CORS(app)

# Load questions from JSON file
def load_questions():
    try:
        with open('questions.json', 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading questions: {e}")
        return None

# API endpoint to get random questions for a specific language
@app.route('/api/quiz', methods=['GET'])
def get_quiz_questions():
    try:
        # Get language from query parameters
        language = request.args.get('language', '').lower()
        
        # Load questions
        questions_data = load_questions()
        if not questions_data:
            return jsonify({
                'success': False,
                'message': 'Error loading questions'
            }), 500

        # Check if language exists
        if language not in questions_data:
            return jsonify({
                'success': False,
                'message': f'Invalid language. Available languages: {", ".join(questions_data.keys())}'
            }), 400

        # Get questions for the specified language
        language_questions = questions_data[language]
        
        # Randomly select 4 questions
        selected_questions = random.sample(language_questions, min(4, len(language_questions)))
        
        # Format response
        response = {
            'success': True,
            'language': language,
            'questions': selected_questions
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error processing request: {str(e)}'
        }), 500

# API endpoint to check answers
@app.route('/api/quiz/check', methods=['POST'])
def check_answers():
    try:
        data = request.json
        language = data.get('language', '').lower()
        answers = data.get('answers', {})
        
        # Load questions
        questions_data = load_questions()
        if not questions_data:
            return jsonify({
                'success': False,
                'message': 'Error loading questions'
            }), 500

        # Get questions for the specified language
        language_questions = questions_data[language]
        
        # Calculate score
        score = 0
        results = []
        
        for question_id, answer in answers.items():
            question = language_questions[int(question_id)]
            is_correct = answer == question['correct']
            if is_correct:
                score += 1
                
            results.append({
                'question_id': question_id,
                'question': question['question'],
                'your_answer': question['options'][answer],
                'correct_answer': question['options'][question['correct']],
                'is_correct': is_correct
            })
        
        # Calculate percentage
        percentage = (score / len(answers)) * 100 if answers else 0
        
        return jsonify({
            'success': True,
            'score': score,
            'total': len(answers),
            'percentage': round(percentage, 2),
            'results': results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error checking answers: {str(e)}'
        }), 500

if __name__ == '__main__':
    app.run(debug=True) 