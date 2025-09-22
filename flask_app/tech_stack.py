from flask import Blueprint, render_template, session, redirect, url_for,jsonify
from groq import Groq


tech_stack = Blueprint('tech_stack', __name__)

GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

@tech_stack.route('/tech_stack_documentation')
def tech_stack_documentation():
    file_data = session.get('file', {})
    if not file_data:
        return redirect(url_for('dashboard.dashboard'))  # Back to dashboard if no file
    filename = next(iter(file_data.keys()))
    content = next(iter(file_data.values()))
    
    # Prompt for tech stack documentation
    prompt = f"""Analyze this code and determine if it contains a detectable tech stack (e.g., languages, frameworks, libraries, databases, or dependencies). If a tech stack is detected, generate a structured documentation in markdown format with the following sections:
    - **Tech Stack Overview**: Provide a high-level overview of the technologies used, including backend, frontend, databases, and key dependencies.
    - **List of Technologies**: Provide a numbered list of detected technologies (e.g., 1. Python 3.x, 2. Flask framework).
    - **Explanation of Technologies**: For each technology, include:
    - **Purpose**: What role it plays in the code (e.g., backend framework, database).
    - **Version**: Detected or inferred version if available (e.g., Flask 2.0+).
    - **Dependencies**: List related dependencies or how it interacts with others.
    - **Example**: Provide a code snippet showing its usage.
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
    
    
    return render_template('tech_stack_documentation.html', result=ai_response, filename=filename)



# 🔄 New API route for AJAX regeneration
@tech_stack.route('/api/regenerate_tech_stack', methods=['POST'])
def regenerate_tech_stack():
    file_data = session.get('file', {})
    if not file_data:
        return jsonify({"error": "No file found in session"}), 400

    filename = next(iter(file_data.keys()))
    content = next(iter(file_data.values()))

    prompt = f"""Analyze this code and determine if it contains a detectable tech stack (e.g., languages, frameworks, libraries, databases, or dependencies). If a tech stack is detected, generate a structured documentation in markdown format with the following sections:
    - **Tech Stack Overview**: Provide a high-level overview of the technologies used, including backend, frontend, databases, and key dependencies.
    - **List of Technologies**: Provide a numbered list of detected technologies (e.g., 1. Python 3.x, 2. Flask framework).
    - **Explanation of Technologies**: For each technology, include:
    - **Purpose**: What role it plays in the code (e.g., backend framework, database).
    - **Version**: Detected or inferred version if available (e.g., Flask 2.0+).
    - **Dependencies**: List related dependencies or how it interacts with others.
    - **Example**: Provide a code snippet showing its usage.
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