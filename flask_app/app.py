from flask import Flask, send_from_directory, request, session, jsonify
from .functiondashboard import bp_dashboard
from .generate import generate
from .validation import validation
from .relationship import relationship 
from .setup import setup 
from .tech_stack import tech_stack 
from .diagram import diagram
from .chatbot import chatbot1
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = os.getenv("FLASK_SECRET_KEY")

# Make session permanent for 24 hours
app.config['PERMANENT_SESSION_LIFETIME'] = 86400

# Register blueprints
app.register_blueprint(bp_dashboard)
app.register_blueprint(generate)
app.register_blueprint(validation)
app.register_blueprint(relationship)
app.register_blueprint(setup)
app.register_blueprint(tech_stack)
app.register_blueprint(diagram)
app.register_blueprint(chatbot1)

# Route for home page
@app.route('/')
def home():
    return send_from_directory('static', 'home.html')

# Route for upload page
@app.route('/upload')
def serve_upload():
    return send_from_directory('static', 'upload.html')

# Route for dashboard
@app.route('/dashboard')
def serve_dashboard():
    return send_from_directory('static', 'dashboard.html')

# IMPORTANT: This endpoint stores files in session for chatbot access
@app.route('/api/set_files', methods=['POST'])
def set_files():
    try:
        session.permanent = True
        data = request.get_json()
        files = data.get('files', [])
        
        if not files:
            return jsonify({'error': 'No files provided'}), 400
        
        # Store files in session with key 'uploaded_files' for chatbot to access
        session['uploaded_files'] = files
        
        print(f"✅ Stored {len(files)} files in session['uploaded_files']")
        print(f"Files: {[f.get('name') for f in files]}")
        
        return jsonify({
            'status': 'success',
            'message': f'Successfully stored {len(files)} files in session',
            'files': [f.get('name') for f in files]
        }), 200
        
    except Exception as e:
        print(f"❌ Error in set_files: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.before_request
def before_request():
    session.permanent = True

if __name__ == '__main__':
    app.run(debug=True)