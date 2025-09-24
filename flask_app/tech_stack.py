from flask import Blueprint, render_template, session, redirect, url_for, jsonify, current_app
from groq import Groq

tech_stack = Blueprint('tech_stack', __name__)

GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

@tech_stack.route('/tech_stack_documentation')
def tech_stack_documentation():
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
    return render_template('tech_stack_documentation.html', result=combined_result, files=files)

@tech_stack.route('/api/regenerate_tech_stack', methods=['POST'])
def regenerate_tech_stack():
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