from flask import Blueprint, request, render_template, jsonify, session
from flask_cors import CORS
from groq import Groq
import json

chatbot1 = Blueprint('chatbot', __name__)
CORS(chatbot1)  # Enable CORS for all routes

GROQ_API_KEY = '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'
client = Groq(api_key=GROQ_API_KEY)

# Store conversations in memory (use a database in production)
conversations = {}

@chatbot1.route('/chatbot')
def index():
    print("Chatbot route accessed")
    
    # Get files from session (keeping your existing session key)
    files = session.get('files', [])
    print(f"Files in session: {len(files) if files else 0}")
    
    # Prepare files for JavaScript (this was missing in your original)
    if files:
        # Clean up file data for frontend
        cleaned_files = []
        for file in files:
            cleaned_file = {
                'name': file.get('name', ''),
                'content': file.get('content', ''),
                'type': file.get('type', 'text/plain')
            }
            cleaned_files.append(cleaned_file)
        
        files_json = json.dumps(cleaned_files)
        print(f"Prepared {len(cleaned_files)} files for frontend")
    else:
        files_json = '[]'
        cleaned_files = files  # Use original files if empty
    
    # Pass both files and files_json to template
    return render_template(
        'chatbot.html',  # Keep your existing template name
        files=cleaned_files,
        files_json=files_json  # This is needed for JavaScript initialization
    )

@chatbot1.route('/api/set_files', methods=['POST'])
def set_files():
    """Receive files from dashboard"""
    try:
        data = request.get_json()
        files = data.get('files', [])
        
        print(f"Received {len(files)} files from dashboard")
        
        if not files:
            return jsonify({'error': 'No files provided'}), 400
        
        # Store files in session for chatbot access
        session['uploaded_files'] = files
        session.permanent = True  # Make session persistent
        
        # Log file names for debugging
        file_names = [f['name'] for f in files]
        print(f"Stored files: {file_names}")
        
        return jsonify({
            'success': True,
            'message': f'Successfully received {len(files)} files',
            'files': file_names
        })
        
    except Exception as e:
        print(f"Error in set_files endpoint: {e}")
        return jsonify({'error': str(e)}), 500

@chatbot1.route('/api/get_files', methods=['GET'])
def get_files():
    """Get current uploaded files from session"""
    try:
        files = session.get('uploaded_files', [])
        
        # Clean up files data
        cleaned_files = []
        for file in files:
            cleaned_files.append({
                'name': file.get('name', ''),
                'content': file.get('content', ''),
                'type': file.get('type', 'text/plain')
            })
        
        print(f"Returning {len(cleaned_files)} files from session")
        
        return jsonify({
            'success': True,
            'files': cleaned_files
        })
    except Exception as e:
        print(f"Error in get_files endpoint: {e}")
        return jsonify({'error': str(e)}), 500

@chatbot1.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages with AI"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        conversation_id = data.get('conversation_id', 'default')
        selected_files = data.get('selected_files', [])
        include_all_files = data.get('include_all_files', True)

        print(f"Chat request - Message: {message[:50]}...")
        print(f"Conversation ID: {conversation_id}")
        print(f"Include all files: {include_all_files}")

        if not message:
            return jsonify({'error': 'No message provided'}), 400

        # Initialize conversation if it doesn't exist
        if conversation_id not in conversations:
            conversations[conversation_id] = []
            
            # Create enhanced system prompt
            system_prompt = """You are an expert code assistant. Your role is to:
            1. Analyze code files and explain their functionality clearly
            2. Answer programming questions with detailed explanations
            3. Suggest improvements and optimizations
            4. Help debug issues and identify potential problems
            5. Provide code examples when helpful
            
            Be concise but thorough. Format code blocks properly and use clear language."""
            
            # Add file context to system prompt
            files = session.get('uploaded_files', [])
            if files:
                file_context = "\n\nYou have access to the following files:\n"
                for file in files:
                    file_context += f"\n📄 {file['name']}"
                    # Add a preview of the file content
                    content_preview = file['content'][:500] if len(file['content']) > 500 else file['content']
                    file_context += f"\nPreview:\n```\n{content_preview}\n```\n"
                    if len(file['content']) > 500:
                        file_context += f"... (file continues, total {len(file['content'])} characters)\n"
                
                system_prompt += file_context
                system_prompt += "\nAlways consider these files when answering questions. Reference specific files by name when relevant."
            
            conversations[conversation_id].append({
                "role": "system", 
                "content": system_prompt
            })
            print(f"Initialized new conversation with {len(files)} files in context")

        # Get all files from session
        files = session.get('uploaded_files', [])
        
        # Enhance message with file context if requested
        enhanced_message = message
        if include_all_files and files:
            # Add context about available files
            file_names = [f['name'] for f in files]
            context_note = f"\n[User is asking about these files: {', '.join(file_names)}]\n"
            
            # If asking about specific files, include their full content
            for file_name in selected_files:
                for file in files:
                    if file['name'] == file_name:
                        context_note += f"\n--- Full content of '{file_name}' ---\n"
                        context_note += file['content']
                        context_note += f"\n--- End of '{file_name}' ---\n"
                        break
            
            enhanced_message = context_note + "\nUser question: " + message

        # Add user message to conversation
        conversations[conversation_id].append({
            "role": "user", 
            "content": enhanced_message
        })

        # Get AI response from Groq
        try:
            chat_completion = client.chat.completions.create(
                messages=conversations[conversation_id],
                model="llama-3.3-70b-versatile",
                max_tokens=2000,  # Increased for detailed responses
                temperature=0.7,
                top_p=0.9
            )

            ai_response = chat_completion.choices[0].message.content
            
            # Format the response for better display
            ai_response = ai_response.replace('```python', '\n```python\n')
            ai_response = ai_response.replace('```javascript', '\n```javascript\n')
            ai_response = ai_response.replace('```java', '\n```java\n')
            ai_response = ai_response.replace('```', '\n```\n')

        except Exception as api_error:
            print(f"Groq API error: {api_error}")
            ai_response = "I apologize, but I'm having trouble connecting to the AI service. Please try again in a moment."

        # Add AI response to conversation
        conversations[conversation_id].append({
            "role": "assistant", 
            "content": ai_response
        })

        # Manage conversation history (keep last 30 messages)
        if len(conversations[conversation_id]) > 31:  # 1 system + 30 messages
            conversations[conversation_id] = (
                conversations[conversation_id][:1] +  # Keep system prompt
                conversations[conversation_id][-30:]   # Keep last 30 messages
            )

        return jsonify({
            'success': True,
            'response': ai_response,
            'conversation_id': conversation_id
        })

    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': 'An error occurred while processing your request.',
            'details': str(e)
        }), 500

@chatbot1.route('/api/clear_conversation', methods=['POST'])
def clear_conversation():
    """Clear conversation history but keep files"""
    try:
        data = request.get_json()
        conversation_id = data.get('conversation_id', 'default')
        
        # Clear the specific conversation
        if conversation_id in conversations:
            del conversations[conversation_id]
            print(f"Cleared conversation: {conversation_id}")
        
        # Files remain in session
        files = session.get('uploaded_files', [])
        
        return jsonify({
            'success': True,
            'message': 'Conversation cleared successfully',
            'files_retained': len(files)
        })
    except Exception as e:
        print(f"Error clearing conversation: {e}")
        return jsonify({'error': str(e)}), 500