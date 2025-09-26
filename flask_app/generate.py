from flask import Blueprint, render_template, session, redirect, url_for, jsonify, current_app
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

    # Initialize result to store documentation for all files
    combined_result = ""

    for file_data in files:
        filename = file_data.get('name', 'Unknown file')
        content = file_data.get('content', '')  # Fallback to empty string if no content

        if not content:
            current_app.logger.warning(f"No content found for file {filename}")
            combined_result += f"## {filename}\nNo content available for documentation\n\n"
            continue

        prompt = f"""Analyze this code and generate a structured documentation in markdown format with the following sections:
        - **Code Structure**: Provide a high-level overview of how the code is organized (e.g., functions and their relationships).
        - **Code Overview**: Describe the general purpose of the program and how to use it.
        - **List of Functions**: Provide a numbered list of all functions (e.g., 1. process_data, 2. validate_input).
        - **Explanation of Functions**: For each function, include:
          - Purpose: What the function does.
          - Parameters: List and describe all parameters.
          - Return Values: Describe what the function returns.
          - Example: Provide a code example with expected output.
        Ensure the output is well-organized and follows this exact structure. Include a header with the filename '{filename}' at the start of the documentation. Here is the code to analyze:\n\n{content}"""

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
            combined_result += f"{ai_response}\n\n"
        except Exception as e:
            current_app.logger.error(f"Error generating documentation for {filename}: {str(e)}")
            combined_result += f"## {filename}\nError generating documentation: {str(e)}\n\n"

    if not combined_result:
        combined_result = "No documentation generated for any files."

    # Pass the combined result and list of files to the template
    return render_template('function_documentation.html', result=combined_result, files=files)

@generate.route('/api/regenerate_doc', methods=['POST'])
def regenerate_doc():
    files = session.get('files', [])
    if not files:
        current_app.logger.warning("No files found in session for /api/regenerate_doc")
        return jsonify({"error": "No files found in session"}), 400

    # Initialize result to store documentation for all files
    combined_result = ""

    for file_data in files:
        filename = file_data.get('name', 'Unknown file')
        content = file_data.get('content', '')

        if not content:
            current_app.logger.warning(f"No content found for file {filename}")
            combined_result += f"## {filename}\nNo content available for documentation\n\n"
            continue

        prompt = f"""Analyze this code and generate a structured documentation in markdown format with the following sections:
        - **Code Structure**: Provide a high-level overview of how the code is organized (e.g., functions and their relationships).
        - **Code Overview**: Describe the general purpose of the program and how to use it.
        - **List of Functions**: Provide a numbered list of all functions (e.g., 1. process_data, 2. validate_input).
        - **Explanation of Functions**: For each function, include:
          - Purpose: What the function does.
          - Parameters: List and describe all parameters.
          - Return Values: Describe what the function returns.
          - Example: Provide a code example with expected output.
        Ensure the output is well-organized and follows this exact structure. Include a header with the filename '{filename}' at the start of the documentation. Here is the code to analyze:\n\n{content}"""

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
            combined_result += f"{ai_response}\n\n"
        except Exception as e:
            current_app.logger.error(f"Error generating documentation for {filename}: {str(e)}")
            combined_result += f"## {filename}\nError generating documentation: {str(e)}\n\n"

    if not combined_result:
        return jsonify({"error": "No documentation generated for any files"}), 400

    return jsonify({"result": combined_result, "files": [{"name": f.get('name', 'Unknown file')} for f in files]})