from flask import Blueprint, render_template, session, redirect, url_for, jsonify, current_app
from groq import Groq
from dotenv import load_dotenv
import os
import time

relationship = Blueprint('relationship', __name__)

load_dotenv()

# Get API key securely
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is missing! Please set it in the .env file.")

client = Groq(api_key=GROQ_API_KEY)

# Constants for content management
MAX_CONTENT_LENGTH = 15000  # Maximum characters to send to API
MAX_FILES_PER_REQUEST = 10    # Process max 10 files at a time

def truncate_content(content, max_length=MAX_CONTENT_LENGTH):
    """Truncate content if it's too long"""
    if len(content) <= max_length:
        return content, False
    
    # Try to truncate at a reasonable point (end of line)
    truncated = content[:max_length]
    last_newline = truncated.rfind('\n')
    if last_newline > max_length * 0.8:  # If we can find a newline in the last 20%
        truncated = truncated[:last_newline]
    
    return truncated, True

def generate_relationship_doc_for_file(filename, content, retry_count=3):
    """Generate relationship documentation for a single file with retry logic"""
    
    # Truncate content if needed
    truncated_content, was_truncated = truncate_content(content)
    
    prompt = f"""
    Generate documentation that fits in a fixed-height scrollable card viewer.
    FORMATTING RULES:
    - Write naturally in complete sentences and paragraphs
    - Keep sentences under 15-20 words each including example
    Analyze this code and generate a structured documentation in markdown format with the following sections to detail the relationships within the code:
    - **Code Structure**: Provide a high-level overview of how the code is organized (e.g., classes, modules, or functions and their relationships).
    - **Code Overview**: Describe the general purpose of the program and how its components interact.
    - **List of Relationships**: Provide a numbered list of detected relationships (e.g., 1. Inheritance: ClassA extends ClassB, 2. Data Flow: VariableX updates VariableY).
    - **Explanation of Relationships**: For each relationship, include:
    - **Type**: Specify the type of relationship (e.g., inheritance, data flow, function dependency).
    - **Involved Components**: Identify the entities involved (e.g., classes, functions, variables).
    - **Impact**: Describe how the relationship affects the code's behavior or data.
    - **Example**: Provide a code example illustrating the relationship with expected outcomes.
    
    {f'Note: Content was truncated due to length. Showing first {MAX_CONTENT_LENGTH} characters.' if was_truncated else ''}
    
    Ensure the output is well-organized and starts with a markdown header '## {filename}' to indicate the file being documented. Focus on identifying and explaining relationships such as inheritance, data dependencies (e.g., how one data update affects another like a + b = c), and function dependencies (e.g., which function needs another to run). Here is the code to analyze:

{truncated_content}"""

    for attempt in range(retry_count):
        try:
            current_app.logger.info(f"Generating relationship docs for {filename} (attempt {attempt + 1}/{retry_count})")
            
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a helpful code documentation assistant."},
                    {"role": "user", "content": prompt},
                ],
                model="llama-3.3-70b-versatile",
                max_tokens=2000,  # Increased from 1000
                temperature=0.3,
                timeout=30  # 30 second timeout
            )
            
            ai_response = chat_completion.choices[0].message.content
            current_app.logger.info(f"Successfully generated relationship docs for {filename}")
            return ai_response, None
            
        except Exception as e:
            error_msg = str(e)
            current_app.logger.error(f"Error generating relationship docs for {filename} (attempt {attempt + 1}): {error_msg}")
            
            if attempt < retry_count - 1:
                # Wait before retrying (exponential backoff)
                wait_time = (attempt + 1) * 2
                current_app.logger.info(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                return None, error_msg
    
    return None, "Failed after multiple retries"

@relationship.route('/relationship_documentation')
def relationship_documentation():
    files = session.get('files', [])
    if not files:
        current_app.logger.warning("No files found in session for /relationship_documentation")
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
        doc_result, error = generate_relationship_doc_for_file(filename, content)
        
        if doc_result:
            combined_result += f"{doc_result}\n\n---\n\n"
            successful_files.append(filename)
        else:
            error_message = f"Error generating documentation: {error}"
            current_app.logger.error(f"Failed to generate relationship docs for {filename}: {error}")
            combined_result += f"## {filename}\n\n**{error_message}**\n\nPlease try regenerating or upload a smaller file.\n\n---\n\n"
            failed_files.append(filename)

    if not combined_result:
        combined_result = "## No Documentation Generated\n\nNo documentation could be generated for any files. Please try uploading smaller files or fewer files at once."

    # Add summary at the beginning
    summary = f"## Relationship Documentation Summary\n\n"
    summary += f"- **Total Files**: {len(files)}\n"
    summary += f"- **Successfully Documented**: {len(successful_files)}\n"
    if failed_files:
        summary += f"- **Failed**: {len(failed_files)} ({', '.join(failed_files)})\n"
    summary += f"\n---\n\n"
    
    combined_result = summary + combined_result

    return render_template('relationship_documentation.html', result=combined_result, files=files)

@relationship.route('/api/regenerate_relationship', methods=['POST'])
def regenerate_relationship():
    files = session.get('files', [])
    if not files:
        current_app.logger.warning("No files found in session for /api/regenerate_relationship")
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
        doc_result, error = generate_relationship_doc_for_file(filename, content)
        
        if doc_result:
            combined_result += f"{doc_result}\n\n---\n\n"
            successful_files.append(filename)
        else:
            error_message = f"Error generating documentation: {error}"
            current_app.logger.error(f"Failed to generate relationship docs for {filename}: {error}")
            combined_result += f"## {filename}\n\n**{error_message}**\n\nPlease try regenerating or upload a smaller file.\n\n---\n\n"
            failed_files.append(filename)

    if not combined_result:
        return jsonify({"error": "No documentation generated for any files"}), 400

    # Add summary
    summary = f"## Relationship Documentation Summary\n\n"
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