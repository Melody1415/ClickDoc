from flask import Blueprint, render_template, session, redirect, url_for,jsonify
from groq import Groq


relationship = Blueprint('relationship', __name__)

GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

@relationship.route('/relationship_documentation')
def relationship_documentation():
    file_data = session.get('file', {})
    if not file_data:
        return redirect(url_for('functiondashboard.dashboard'))  # Back to dashboard if no file
    filename = next(iter(file_data.keys()))
    content = next(iter(file_data.values()))
    
    # Prompt for relationship documentation
    prompt = f"""Analyze this code and generate a structured documentation in markdown format with the following sections to detail the relationships within the code:
    - **Code Structure**: Provide a high-level overview of how the code is organized (e.g., classes, modules, or functions and their relationships).
    - **Code Overview**: Describe the general purpose of the program and how its components interact.
    - **List of Relationships**: Provide a numbered list of detected relationships (e.g., 1. Inheritance: ClassA extends ClassB, 2. Data Flow: VariableX updates VariableY).
    - **Explanation of Relationships**: For each relationship, include:
    - **Type**: Specify the type of relationship (e.g., inheritance, data flow, function dependency).
    - **Involved Components**: Identify the entities involved (e.g., classes, functions, variables).
    - **Impact**: Describe how the relationship affects the code's behavior or data.
    - **Example**: Provide a code example illustrating the relationship with expected outcomes.
    Ensure the output is well-organized and focuses on identifying and explaining relationships such as inheritance, data dependencies (e.g., how one data update affects another like a + b = c), and function dependencies (e.g., which function needs another to run). Here is the code to analyze:\n\n{content}"""    

    
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
    
    
    return render_template('relationship_documentation.html', result=ai_response, filename=filename)



# 🔄 New API route for AJAX regeneration
@relationship.route('/api/regenerate_relationship', methods=['POST'])
def regenerate_relationship():
    file_data = session.get('file', {})
    if not file_data:
        return jsonify({"error": "No file found in session"}), 400

    filename = next(iter(file_data.keys()))
    content = next(iter(file_data.values()))

    prompt = f"""Analyze this code and generate a structured documentation in markdown format with the following sections to detail the relationships within the code:
    - **Code Structure**: Provide a high-level overview of how the code is organized (e.g., classes, modules, or functions and their relationships).
    - **Code Overview**: Describe the general purpose of the program and how its components interact.
    - **List of Relationships**: Provide a numbered list of detected relationships (e.g., 1. Inheritance: ClassA extends ClassB, 2. Data Flow: VariableX updates VariableY).
    - **Explanation of Relationships**: For each relationship, include:
    - **Type**: Specify the type of relationship (e.g., inheritance, data flow, function dependency).
    - **Involved Components**: Identify the entities involved (e.g., classes, functions, variables).
    - **Impact**: Describe how the relationship affects the code's behavior or data.
    - **Example**: Provide a code example illustrating the relationship with expected outcomes.
    Ensure the output is well-organized and focuses on identifying and explaining relationships such as inheritance, data dependencies (e.g., how one data update affects another like a + b = c), and function dependencies (e.g., which function needs another to run). Here is the code to analyze:\n\n{content}"""

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