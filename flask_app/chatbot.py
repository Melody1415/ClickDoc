from flask import Blueprint, request, render_template, jsonify, session
from flask_cors import CORS
from groq import Groq
from dotenv import load_dotenv
import os
import json
import base64

chatbot1 = Blueprint('chatbot', __name__)
CORS(chatbot1)

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is missing! Please set it in the .env file.")

client = Groq(api_key=GROQ_API_KEY)

conversations = {}

@chatbot1.route('/chatbot')
def index():
    print("Chatbot route accessed")
    
    # Get files from session
    files = session.get('files', [])
    print(f"Files in session: {len(files) if files else 0}")
    
    # Prepare files for JavaScript
    if files:
        cleaned_files = []
        for file in files:
            # Decode base64 content if it exists
            content = file.get('content', '')
            if content:
                try:
                    # Try to decode if it's base64
                    content = base64.b64decode(content).decode('utf-8')
                except:
                    # If decoding fails, use as-is
                    pass
            
            cleaned_file = {
                'name': file.get('name', ''),
                'content': content,
                'type': file.get('type', 'text/plain')
            }
            cleaned_files.append(cleaned_file)
        
        files_json = json.dumps(cleaned_files)
        print(f"✅ Prepared {len(cleaned_files)} files for frontend")
    else:
        files_json = '[]'
        cleaned_files = []
        print("⚠️ No files found in session")
    
    return render_template(
        'chatbot.html',
        files=cleaned_files,
        files_json=files_json
    )

@chatbot1.route('/api/set_files', methods=['POST'])
def set_files():
    """Receive files from dashboard or upload page"""
    try:
        data = request.get_json()
        files = data.get('files', [])
        
        print(f"📥 Received {len(files)} files")
        
        if not files:
            return jsonify({'error': 'No files provided'}), 400
        
        # Process and store files in session
        processed_files = []
        for file in files:
            processed_file = {
                'name': file.get('name', ''),
                'content': file.get('content', ''),
                'type': file.get('type', 'text/plain')
            }
            processed_files.append(processed_file)
        
        # Store in session with both keys for compatibility
        session['files'] = processed_files
        session['uploaded_files'] = processed_files
        session.permanent = True
        
        file_names = [f['name'] for f in processed_files]
        print(f"✅ Stored files in session: {file_names}")
        
        return jsonify({
            'success': True,
            'message': f'Successfully received {len(processed_files)} files',
            'files': file_names
        })
        
    except Exception as e:
        print(f"❌ Error in set_files endpoint: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@chatbot1.route('/api/get_files', methods=['GET'])
def get_files():
    """Get current uploaded files from session"""
    try:
        # Try both session keys
        files = session.get('uploaded_files', session.get('files', []))
        
        cleaned_files = []
        for file in files:
            content = file.get('content', '')
            # Decode base64 if needed
            if content:
                try:
                    content = base64.b64decode(content).decode('utf-8')
                except:
                    pass
            
            cleaned_files.append({
                'name': file.get('name', ''),
                'content': content,
                'type': file.get('type', 'text/plain')
            })
        
        print(f"📤 Returning {len(cleaned_files)} files from session")
        
        return jsonify({
            'success': True,
            'files': cleaned_files
        })
    except Exception as e:
        print(f"❌ Error in get_files endpoint: {e}")
        return jsonify({'error': str(e)}), 500

@chatbot1.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages with AI - Enhanced formatting"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        conversation_id = data.get('conversation_id', 'default')
        selected_files = data.get('selected_files', [])
        include_all_files = data.get('include_all_files', True)

        print(f"💬 Chat request - Message: {message[:50]}...")
        print(f"🔑 Conversation ID: {conversation_id}")

        if not message:
            return jsonify({'error': 'No message provided'}), 400

        # Initialize conversation if it doesn't exist
        if conversation_id not in conversations:
            conversations[conversation_id] = []
            
            # ENHANCED: Better system prompt for formatting
            system_prompt = """You are an expert code assistant with excellent communication skills. Your role is to:

1. Analyze code files and explain their functionality clearly
2. Answer programming questions with detailed, well-structured explanations
3. Suggest improvements and optimizations
4. Help debug issues and identify potential problems
5. Provide code examples when helpful

**IMPORTANT FORMATTING RULES:**
- Use markdown formatting for better readability
- Break down long explanations into clear sections
- Use bullet points (- or *) for lists
- Use numbered lists (1., 2., 3.) for sequential steps
- Use **bold** for important terms and concepts
- Use `inline code` for short code snippets
- Use code blocks with language tags for longer code:
  ```python
  def example():
      return "code here"
  ```
- Add blank lines between sections for better readability
- Use headers (##) to organize your response into sections
- Keep paragraphs short and focused (2-4 sentences max)
- Highlight key points and actionable items

Be concise but thorough. Make your responses scannable and easy to read."""
            
            # Add file context to system prompt
            files = session.get('uploaded_files', session.get('files', []))
            if files:
                file_context = "\n\n📁 **Available Files:**\n"
                for file in files:
                    content = file.get('content', '')
                    # Decode base64 if needed
                    if content:
                        try:
                            content = base64.b64decode(content).decode('utf-8')
                        except:
                            pass
                    
                    file_context += f"\n### 📄 {file['name']}\n"
                    content_preview = content[:300] if len(content) > 300 else content
                    file_context += f"```\n{content_preview}\n```\n"
                    if len(content) > 300:
                        file_context += f"... (file continues, total {len(content)} characters)\n"
                
                system_prompt += file_context
                system_prompt += "\n⚡ **Instructions:** Always consider these files when answering. Reference specific files by name when relevant. Format your responses for maximum readability."
            
            conversations[conversation_id].append({
                "role": "system", 
                "content": system_prompt
            })
            print(f"✅ Initialized conversation with {len(files)} files in context")

        # Get all files from session
        files = session.get('uploaded_files', session.get('files', []))
        
        # Enhance message with file context if requested
        enhanced_message = message
        if include_all_files and files:
            file_names = [f['name'] for f in files]
            context_note = f"\n[Context: User is asking about these files: {', '.join(file_names)}]\n"
            
            # If asking about specific files, include their full content
            for file_name in selected_files:
                for file in files:
                    if file['name'] == file_name:
                        content = file.get('content', '')
                        # Decode base64 if needed
                        if content:
                            try:
                                content = base64.b64decode(content).decode('utf-8')
                            except:
                                pass
                        
                        context_note += f"\n--- Full content of '{file_name}' ---\n"
                        context_note += content
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
                max_tokens=2000,
                temperature=0.7,
                top_p=0.9
            )

            ai_response = chat_completion.choices[0].message.content
            
            print(f"✅ AI Response generated ({len(ai_response)} chars)")

        except Exception as api_error:
            print(f"❌ Groq API error: {api_error}")
            ai_response = "I apologize, but I'm having trouble connecting to the AI service. Please try again in a moment."

        # Add AI response to conversation
        conversations[conversation_id].append({
            "role": "assistant", 
            "content": ai_response
        })

        # Manage conversation history (keep last 30 messages)
        if len(conversations[conversation_id]) > 31:
            conversations[conversation_id] = (
                conversations[conversation_id][:1] +
                conversations[conversation_id][-30:]
            )

        return jsonify({
            'success': True,
            'response': ai_response,
            'conversation_id': conversation_id
        })

    except Exception as e:
        print(f"❌ Error in chat endpoint: {e}")
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
        
        if conversation_id in conversations:
            del conversations[conversation_id]
            print(f"🗑️ Cleared conversation: {conversation_id}")
        
        files = session.get('uploaded_files', session.get('files', []))
        
        return jsonify({
            'success': True,
            'message': 'Conversation cleared successfully',
            'files_retained': len(files)
        })
    except Exception as e:
        print(f"❌ Error clearing conversation: {e}")
        return jsonify({'error': str(e)}), 500