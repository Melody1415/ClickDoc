from flask import Flask, send_from_directory, request, session, jsonify
from functiondashboard import bp_dashboard
from generate import generate
from validation import validation
from relationship import relationship 
from setup import setup 
from tech_stack import tech_stack 
from diagram import diagram
from chatbot import chatbot1
from dotenv import load_dotenv
import os
import logging
import hashlib
import json

load_dotenv()

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = os.getenv("FLASK_SECRET_KEY")

# Configure session to handle larger data
app.config['SESSION_TYPE'] = 'filesystem'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app.register_blueprint(bp_dashboard)
app.register_blueprint(generate)
app.register_blueprint(validation)
app.register_blueprint(relationship)
app.register_blueprint(setup)
app.register_blueprint(tech_stack)
app.register_blueprint(diagram)
app.register_blueprint(chatbot1)

# Centralized file storage endpoint
@app.route('/api/set_files', methods=['POST'])
def set_files():
    """Centralized endpoint to store files in session"""
    try:
        data = request.get_json()
        files = data.get('files', [])
        
        if not files:
            logger.warning("No files provided in request")
            return jsonify({'error': 'No files provided'}), 400
        
        # Validate and process files
        processed_files = []
        total_size = 0
        max_file_size = 5 * 1024 * 1024  # 5MB per file limit
        
        for file in files:
            # Validate file structure
            if not isinstance(file, dict) or 'name' not in file:
                logger.warning(f"Invalid file structure: {file}")
                continue
            
            # Get file content
            content = file.get('content', '')
            
            # Check file size
            content_size = len(content.encode('utf-8'))
            if content_size > max_file_size:
                logger.warning(f"File {file['name']} exceeds size limit: {content_size} bytes")
                return jsonify({
                    'error': f"File {file['name']} is too large. Maximum size is 5MB per file."
                }), 400
            
            total_size += content_size
            
            # Process file
            processed_file = {
                'name': file['name'],
                'content': content,
                'size': content_size,
                'type': file.get('type', 'text/plain'),
                'checksum': hashlib.md5(content.encode('utf-8')).hexdigest()
            }
            processed_files.append(processed_file)
        
        # Check total size (max 20MB for all files combined)
        if total_size > 20 * 1024 * 1024:
            return jsonify({
                'error': 'Total file size exceeds 20MB. Please upload fewer or smaller files.'
            }), 400
        
        # Store in session
        session['files'] = processed_files
        session.modified = True
        
        # Create session ID for tracking
        session_id = hashlib.md5(
            json.dumps([f['checksum'] for f in processed_files]).encode()
        ).hexdigest()[:16]
        
        logger.info(f"Stored {len(processed_files)} files in session. Session ID: {session_id}")
        
        return jsonify({
            'status': 'success',
            'file_count': len(processed_files),
            'total_size': total_size,
            'session_id': session_id,
            'files': [{'name': f['name'], 'size': f['size']} for f in processed_files]
        }), 200
        
    except Exception as e:
        logger.error(f"Error in set_files: {str(e)}", exc_info=True)
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/get_files', methods=['GET'])
def get_files():
    """Get files from session"""
    try:
        files = session.get('files', [])
        logger.info(f"Retrieved {len(files)} files from session")
        
        return jsonify({
            'success': True,
            'files': files,
            'count': len(files)
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_files: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/clear_files', methods=['POST'])
def clear_files():
    """Clear files from session"""
    try:
        session.pop('files', None)
        session.modified = True
        logger.info("Cleared files from session")
        
        return jsonify({'status': 'success'}), 200
        
    except Exception as e:
        logger.error(f"Error clearing files: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

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

# Health check endpoint
@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'session_active': 'files' in session,
        'file_count': len(session.get('files', []))
    }), 200

if __name__ == '__main__':
    app.run(debug=True)