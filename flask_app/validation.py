from flask import Blueprint, render_template, session, redirect, url_for, jsonify, current_app
from groq import Groq
from dotenv import load_dotenv
import os

validation = Blueprint('validation', __name__)

load_dotenv()

# Get API key securely
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is missing! Please set it in the .env file.")

client = Groq(api_key=GROQ_API_KEY)

@validation.route('/validation_documentation')
def validation_documentation():
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

         # Prompt for validation documentation
        prompt = f"""Analyze this code and determine if it contains a form (e.g., HTML form elements or form-related validation logic). If it is a form, generate a structured documentation in markdown format with the following sections:
        - **Form Overview**: Describe the purpose of the form and its general validation approach.
        - **Field Validations**: List each field with:
        - **Field Name**: The name or identifier of the field.
        - **Validation Rules**: Specify required rules (e.g., required, min/max length, pattern, data type).
        - **Error Handling**: Describe how errors are handled or displayed.
        - **Example**: Provide an example of valid and invalid input with expected outcomes.
        Ensure the output is well-organized and focuses on form validation details.

        If the code is not a form, check for any general validation logic (e.g., data type checks, range validation). If no validation is detected, return the message: "Since this is not a form file, no validation detected." If validation logic is present, generate a structured documentation with:
        - **Validation Overview**: Summarize the purpose and scope of the validation.
        - **Validation Rules**: List detected validation checks (e.g., type, range, conditions) with descriptions.
        - **Example**: Provide an example of the validation in action with expected outcomes.
        Ensure the output is well-organized and focuses on form validation details.
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
    return render_template('validation_documentation.html', result=combined_result, files=files)

@validation.route('/api/regenerate_validation', methods=['POST'])
def regenerate_validation():
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

        prompt = f"""Analyze this code and determine if it contains a form (e.g., HTML form elements or form-related validation logic). If it is a form, generate a structured documentation in markdown format with the following sections:
        - **Form Overview**: Describe the purpose of the form and its general validation approach.
        - **Field Validations**: List each field with:
        - **Field Name**: The name or identifier of the field.
        - **Validation Rules**: Specify required rules (e.g., required, min/max length, pattern, data type).
        - **Error Handling**: Describe how errors are handled or displayed.
        **Example**: Provide an example of valid and invalid input with expected outcomes.
        Ensure the output is well-organized and focuses on form validation details.

        If the code is not a form, check for any general validation logic (e.g., data type checks, range validation). If no validation is detected, return the message: "Since this is not a form file, no validation detected." If validation logic is present, generate a structured documentation with:
        - **Validation Overview**: Summarize the purpose and scope of the validation.
        - **Validation Rules**: List detected validation checks (e.g., type, range, conditions) with descriptions.
        - **Example**: Provide an example of the validation in action with expected outcomes.
        Ensure the output is well-organized and focuses on form validation details.
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