from flask import Blueprint, render_template, session, redirect, url_for, jsonify, current_app
from groq import Groq
from dotenv import load_dotenv
import os

setup = Blueprint('setup', __name__)

load_dotenv()

# Get API key securely
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is missing! Please set it in the .env file.")

client = Groq(api_key=GROQ_API_KEY)

@setup.route('/setup_documentation')
def setup_documentation():
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

        # Prompt for setup documentation
        prompt = f"""Analyze this code and determine if it requires a setup guide (e.g., dependencies to install, environment configuration, or steps to run). If setup is required, generate a structured setup guide in markdown format with the following sections:
        Generate documentation that fits in a fixed-height scrollable card viewer.
          FORMATTING RULES:
        - Write naturally in complete sentences and paragraphs
        - Keep sentences under 15-20 words each including example 
        - **Setup Overview**: Provide a high-level overview of the setup process and requirements.
        - **Installation Steps**: List detailed steps to install dependencies (e.g., pip install for Python packages).
        - **Configuration**: Describe any configuration needed (e.g., environment variables, folders to create).
        - **Running the Code**: Provide step-by-step instructions on how to run the code, including commands.
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
    return render_template('setup_documentation.html', result=combined_result, files=files)

@setup.route('/api/regenerate_setup', methods=['POST'])
def regenerate_setup():
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

        prompt = f"""Analyze this code and determine if it requires a setup guide (e.g., dependencies to install, environment configuration, or steps to run). If setup is required, generate a structured setup guide in markdown format with the following sections:
        Generate documentation that fits in a fixed-height scrollable card viewer.
          FORMATTING RULES:
        - Write naturally in complete sentences and paragraphs
        - Keep sentences under 15-20 words each including example 
        - **Setup Overview**: Provide a high-level overview of the setup process and requirements.
        - **Installation Steps**: List detailed steps to install dependencies (e.g., pip install for Python packages).
        - **Configuration**: Describe any configuration needed (e.g., environment variables, folders to create).
        - **Running the Code**: Provide step-by-step instructions on how to run the code, including commands.
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