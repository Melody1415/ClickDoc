from flask import Blueprint, render_template, session, redirect, url_for,jsonify
from groq import Groq


setup = Blueprint('setup', __name__)

GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

@setup.route('/setup_documentation')
def setup_documentation():
    file_data = session.get('file', {})
    if not file_data:
        return redirect(url_for('dashboard.dashboard'))  # Back to dashboard if no file
    filename = next(iter(file_data.keys()))
    content = next(iter(file_data.values()))
    
    # Prompt for setup documentation
    prompt = f"""Analyze this code and determine if it requires a setup guide (e.g., dependencies to install, environment configuration, or steps to run). If setup is required, generate a structured setup guide in markdown format with the following sections:
    - **Setup Overview**: Provide a high-level overview of the setup process and requirements.
    - **Installation Steps**: List detailed steps to install dependencies (e.g., pip install for Python packages).
    - **Configuration**: Describe any configuration needed (e.g., environment variables, folders to create).
    - **Running the Code**: Provide step-by-step instructions on how to run the code, including commands.
    Ensure the output is concise, well-organized, and follows this exact structure.

    Here is the code to analyze:\n\n{content}"""    

    
    # Call Groq
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful code documentation assistant."},
            {"role": "user", "content": prompt},
        ],
        model="llama-3.3-70b-versatile",
        max_tokens=1000
    )
    ai_response = chat_completion.choices[0].message.content
    
    
    return render_template('setup_documentation.html', result=ai_response, filename=filename)



# 🔄 New API route for AJAX regeneration
@setup.route('/api/regenerate_setup', methods=['POST'])
def regenerate_setup():
    file_data = session.get('file', {})
    if not file_data:
        return jsonify({"error": "No file found in session"}), 400

    filename = next(iter(file_data.keys()))
    content = next(iter(file_data.values()))

    prompt = f"""Analyze this code and determine if it requires a setup guide (e.g., dependencies to install, environment configuration, or steps to run). If setup is required, generate a structured setup guide in markdown format with the following sections:
    - **Setup Overview**: Provide a high-level overview of the setup process and requirements.
    - **Installation Steps**: List detailed steps to install dependencies (e.g., pip install for Python packages).
    - **Configuration**: Describe any configuration needed (e.g., environment variables, folders to create).
    - **Running the Code**: Provide step-by-step instructions on how to run the code, including commands.
    Ensure the output is concise, well-organized, and follows this exact structure.

    Here is the code to analyze:\n\n{content}"""

    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful code documentation assistant."},
            {"role": "user", "content": prompt},
        ],
        model="llama-3.3-70b-versatile",
        max_tokens=1000
    )
    ai_response = chat_completion.choices[0].message.content

    return jsonify({"result": ai_response, "filename": filename})