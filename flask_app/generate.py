from flask import Blueprint, render_template, session, redirect, url_for, jsonify,current_app
from groq import Groq

generate = Blueprint('generate', __name__)

GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)



@generate.route('/function_documentation')
def function_documentation():
    files = session.get('files', [])
    if not files:
        current_app.logger.warning("No files found in session for /function_documentation")
        return redirect(url_for('functiondashboard.dashboard'))

    # Use the first file for documentation
    file_data = files[0]
    filename = file_data.get('name', 'Unknown file')
    content = file_data.get('content', '')  # Fallback to empty string if no content

    if not content:
        current_app.logger.warning(f"No content found for file {filename}")
        return render_template('function_documentation.html', result="No content available for documentation", filename=filename, files=files)

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

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful code documentation assistant."},
                {"role": "user", "content": prompt},
            ],
            model="llama-3.3-70b-versatile",
            max_tokens=1000
        )
        ai_response = chat_completion.choices[0].message.content
    except Exception as e:
        current_app.logger.error(f"Error generating documentation: {str(e)}")
        ai_response = f"Error generating documentation: {str(e)}"

    return render_template('function_documentation.html', result=ai_response, filename=filename, files=files)

@generate.route('/api/regenerate_doc', methods=['POST'])
def regenerate_doc():
    files = session.get('files', [])
    if not files:
        current_app.logger.warning("No files found in session for /api/regenerate_doc")
        return jsonify({"error": "No files found in session"}), 400

    file_data = files[0]
    filename = file_data.get('name', 'Unknown file')
    content = file_data.get('content', '')

    if not content:
        current_app.logger.warning(f"No content found for file {filename}")
        return jsonify({"error": f"No content available for file {filename}"}), 400

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

    try:
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
    except Exception as e:
        current_app.logger.error(f"Error in regenerate_doc: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500