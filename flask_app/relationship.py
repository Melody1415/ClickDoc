from flask import Blueprint, render_template, session, redirect, url_for, jsonify, current_app
from groq import Groq
from dotenv import load_dotenv
import os

relationship = Blueprint('relationship', __name__)

load_dotenv()

# Get API key securely
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is missing! Please set it in the .env file.")

client = Groq(api_key=GROQ_API_KEY)

@relationship.route('/relationship_documentation')
def relationship_documentation():
    files = session.get('files', [])
    if not files:
        current_app.logger.warning("No files found in session for /relationship_documentation")
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

        # Prompt for relationship documentation with filename header instruction
        prompt = f"""
       Generate CONCISE documentation that fits in a fixed-height scrollable card viewer.
         FORMATTING RULES:
        - Write naturally in complete sentences and paragraphs
        - Keep sentences under 15-20 words each
        - Code examples: MAX 3 lines, 70 characters per line
        Analyze this code and generate a structured documentation in markdown format with the following sections to detail the relationships within the code:
        - **Code Structure**: Provide a high-level overview of how the code is organized (e.g., classes, modules, or functions and their relationships).
        - **Code Overview**: Describe the general purpose of the program and how its components interact.
        - **List of Relationships**: Provide a numbered list of detected relationships (e.g., 1. Inheritance: ClassA extends ClassB, 2. Data Flow: VariableX updates VariableY).
        - **Explanation of Relationships**: For each relationship, include:
        - **Type**: Specify the type of relationship (e.g., inheritance, data flow, function dependency).
        - **Involved Components**: Identify the entities involved (e.g., classes, functions, variables).
        - **Impact**: Describe how the relationship affects the code's behavior or data.
        - **Example**: Provide a code example illustrating the relationship with expected outcomes.
        Ensure the output is well-organized and starts with a markdown header '## {filename}' to indicate the file being documented. Focus on identifying and explaining relationships such as inheritance, data dependencies (e.g., how one data update affects another like a + b = c), and function dependencies (e.g., which function needs another to run). Here is the code to analyze:\n\n{content}"""

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
    return render_template('relationship_documentation.html', result=combined_result, files=files)

@relationship.route('/api/regenerate_relationship', methods=['POST'])
def regenerate_relationship():
    files = session.get('files', [])
    if not files:
        current_app.logger.warning("No files found in session for /api/regenerate_relationship")
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

        # Prompt for relationship documentation with filename header instruction
        prompt = f"""
        Generate CONCISE documentation that fits in a fixed-height scrollable card viewer.
          FORMATTING RULES:
        - Write naturally in complete sentences and paragraphs
        - Keep sentences under 15-20 words each
        - Code examples: MAX 3 lines, 70 characters per line
        Analyze this code and generate a structured documentation in markdown format with the following sections to detail the relationships within the code:
        - **Code Structure**: Provide a high-level overview of how the code is organized (e.g., classes, modules, or functions and their relationships).
        - **Code Overview**: Describe the general purpose of the program and how its components interact.
        - **List of Relationships**: Provide a numbered list of detected relationships (e.g., 1. Inheritance: ClassA extends ClassB, 2. Data Flow: VariableX updates VariableY).
        - **Explanation of Relationships**: For each relationship, include:
        - **Type**: Specify the type of relationship (e.g., inheritance, data flow, function dependency).
        - **Involved Components**: Identify the entities involved (e.g., classes, functions, variables).
        - **Impact**: Describe how the relationship affects the code's behavior or data.
        - **Example**: Provide a code example illustrating the relationship with expected outcomes.
        Ensure the output is well-organized and starts with a markdown header '## {filename}' to indicate the file being documented. Focus on identifying and explaining relationships such as inheritance, data dependencies (e.g., how one data update affects another like a + b = c), and function dependencies (e.g., which function needs another to run). Here is the code to analyze:\n\n{content}"""

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