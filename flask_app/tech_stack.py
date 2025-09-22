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
    prompt = f"""Analyze this code and generate a structured documentation in markdown format with the following sections:
    - **Code Structure**: Provide a high-level overview of how the code is organized (e.g., functions and their relationships).
    - **Code Overview**: Describe the general purpose of the program and how to use it.
    - **List of Functions**: Provide a numbered list of all functions (e.g., 1. process_data, 2. validate_input).
    - **Explanation of Functions**: For each function, include:
      - Purpose: What the function does.
      - Parameters: List and describe all parameters.
      - Return Values: Describe what the function returns.
      - Example: Provide a code example with expected output.
    Ensure the output is well-organized and follows this exact structure. Here is the code to analyze:\n\n{content}"""    

    
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
@tech_stack.route('/api/regenerate_doc', methods=['POST'])
def regenerate_doc():
    file_data = session.get('file', {})
    if not file_data:
        return jsonify({"error": "No file found in session"}), 400

    filename = next(iter(file_data.keys()))
    content = next(iter(file_data.values()))

    prompt = f"""Analyze this code and generate structured documentation in markdown format with:
    - **Code Structure**
    - **Code Overview**
    - **List of Functions**
    - **Explanation of Functions**
    Here is the code:\n\n{content}"""

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