from flask import Blueprint, render_template, session, redirect, url_for, jsonify, current_app
from groq import Groq
from dotenv import load_dotenv
import os
import time

validation = Blueprint('validation', __name__)

load_dotenv()

# Get API key securely
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is missing! Please set it in the .env file.")

client = Groq(api_key=GROQ_API_KEY)

# Constants for content management
MAX_CONTENT_LENGTH = 15000 # Maximum characters to send to API
MAX_FILES_PER_REQUEST = 10 # Process max 10 files at a time

def truncate_content(content, max_length=MAX_CONTENT_LENGTH):
    """Truncate content if it's too long"""
    if len(content) <= max_length:
        return content, False
    
    truncated = content[:max_length]
    last_newline = truncated.rfind('\n')
    if last_newline > max_length * 0.8:
        truncated = truncated[:last_newline]
    
    return truncated, True

def generate_validation_doc_for_file(filename, content, retry_count=3):
    """Generate validation documentation for a single file with retry logic"""
    
    truncated_content, was_truncated = truncate_content(content)
    
    prompt = f"""Analyze this code and determine if it contains a form (e.g., HTML form elements or form-related validation logic). If it is a form, generate a structured documentation in markdown format with the following sections:
    Generate documentation that fits in a fixed-height scrollable card viewer.
    FORMATTING RULES:
    - Write naturally in complete sentences and paragraphs
    - Keep sentences under 15-20 words each including example
    - **Form Overview**: Describe the purpose of the form and its general validation approach.
    - **Field Validations**: List each field with:
    - **Field Name**: The name or identifier of the field.
    - **Validation Rules**: Specify required rules (e.g., required, min/max length, pattern, data type).
    - **Error Handling**: Describe how errors are handled or displayed.
    - **Example**: Provide an example of valid and invalid input with expected outcomes.
    
    If the code is not a form, check for any general validation logic (e.g., data type checks, range validation). If no validation is detected, return the message: "Since this is not a form file, no validation detected." If validation logic is present, generate a structured documentation with:
    - **Validation Overview**: Summarize the purpose and scope of the validation.
    - **Validation Rules**: List detected validation checks (e.g., type, range, conditions) with descriptions.
    - **Example**: Provide an example of the validation in action with expected outcomes.
    
    {f'Note: Content was truncated due to length. Showing first {MAX_CONTENT_LENGTH} characters.' if was_truncated else ''}
    
    Ensure the output is well-organized and focuses on form validation details.
    Here is the code to analyze:

{truncated_content}"""

    for attempt in range(retry_count):
        try:
            current_app.logger.info(f"Generating validation docs for {filename} (attempt {attempt + 1}/{retry_count})")
            
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a helpful code documentation assistant."},
                    {"role": "user", "content": prompt},
                ],
                model="llama-3.3-70b-versatile",
                max_tokens=2000,
                temperature=0.3,
                timeout=30
            )
            
            ai_response = chat_completion.choices[0].message.content
            current_app.logger.info(f"Successfully generated validation docs for {filename}")
            return ai_response, None
            
        except Exception as e:
            error_msg = str(e)
            current_app.logger.error(f"Error generating validation docs for {filename} (attempt {attempt + 1}): {error_msg}")
            
            if attempt < retry_count - 1:
                wait_time = (attempt + 1) * 2
                current_app.logger.info(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                return None, error_msg
    
    return None, "Failed after multiple retries"

@validation.route('/validation_documentation')
def validation_documentation():
    files = session.get('files', [])
    if not files:
        current_app.logger.warning("No files found in session for /validation_documentation")
        return redirect(url_for('functiondashboard.dashboard'))

    # Limit number of files
    if len(files) > MAX_FILES_PER_REQUEST:
        current_app.logger.warning(f"Too many files ({len(files)}). Limiting to {MAX_FILES_PER_REQUEST}")
        files = files[:MAX_FILES_PER_REQUEST]
        session['files'] = files

    combined_result = ""
    successful_files = []
    failed_files = []

    for file_data in files:
        filename = file_data.get('name', 'Unknown file')
        content = file_data.get('content', '')

        if not content or not content.strip():
            current_app.logger.warning(f"No content found for file {filename}")
            combined_result += f"## {filename}\n\n**No content available for documentation**\n\n---\n\n"
            failed_files.append(filename)
            continue

        # Generate documentation with retry logic
        doc_result, error = generate_validation_doc_for_file(filename, content)
        
        if doc_result:
            combined_result += f"{doc_result}\n\n---\n\n"
            successful_files.append(filename)
        else:
            error_message = f"Error generating documentation: {error}"
            current_app.logger.error(f"Failed to generate validation docs for {filename}: {error}")
            combined_result += f"## {filename}\n\n**{error_message}**\n\nPlease try regenerating or upload a smaller file.\n\n---\n\n"
            failed_files.append(filename)

    if not combined_result:
        combined_result = "## No Documentation Generated\n\nNo documentation could be generated for any files. Please try uploading smaller files or fewer files at once."

    # Add summary at the beginning
    summary = f"## Validation Documentation Summary\n\n"
    summary += f"- **Total Files**: {len(files)}\n"
    summary += f"- **Successfully Documented**: {len(successful_files)}\n"
    if failed_files:
        summary += f"- **Failed**: {len(failed_files)} ({', '.join(failed_files)})\n"
    summary += f"\n---\n\n"
    
    combined_result = summary + combined_result

    return render_template('validation_documentation.html', result=combined_result, files=files)

@validation.route('/api/regenerate_validation', methods=['POST'])
def regenerate_validation():
    files = session.get('files', [])
    if not files:
        current_app.logger.warning("No files found in session for /api/regenerate_validation")
        return jsonify({"error": "No files found in session"}), 400

    # Limit number of files
    if len(files) > MAX_FILES_PER_REQUEST:
        files = files[:MAX_FILES_PER_REQUEST]

    combined_result = ""
    successful_files = []
    failed_files = []

    for file_data in files:
        filename = file_data.get('name', 'Unknown file')
        content = file_data.get('content', '')

        if not content or not content.strip():
            current_app.logger.warning(f"No content found for file {filename}")
            combined_result += f"## {filename}\n\n**No content available for documentation**\n\n---\n\n"
            failed_files.append(filename)
            continue

        # Generate documentation with retry logic
        doc_result, error = generate_validation_doc_for_file(filename, content)
        
        if doc_result:
            combined_result += f"{doc_result}\n\n---\n\n"
            successful_files.append(filename)
        else:
            error_message = f"Error generating documentation: {error}"
            current_app.logger.error(f"Failed to generate validation docs for {filename}: {error}")
            combined_result += f"## {filename}\n\n**{error_message}**\n\nPlease try regenerating or upload a smaller file.\n\n---\n\n"
            failed_files.append(filename)

    if not combined_result:
        return jsonify({"error": "No documentation generated for any files"}), 400

    # Add summary
    summary = f"## Validation Documentation Summary\n\n"
    summary += f"- **Total Files**: {len(files)}\n"
    summary += f"- **Successfully Documented**: {len(successful_files)}\n"
    if failed_files:
        summary += f"- **Failed**: {len(failed_files)} ({', '.join(failed_files)})\n"
    summary += f"\n---\n\n"
    
    combined_result = summary + combined_result

    return jsonify({
        "result": combined_result,
        "files": [{"name": f.get('name', 'Unknown file')} for f in files],
        "successful": len(successful_files),
        "failed": len(failed_files)
    })