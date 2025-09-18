from flask import Blueprint, render_template, session, redirect, url_for
from groq import Groq

validation = Blueprint('validation', __name__)

GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

@validation.route('/validation_documentation')
def validation_documentation():
    file_data = session.get('file', {})
    if not file_data:
        return redirect(url_for('dashboard.dashboard'))  # Back to dashboard if no file
    filename = next(iter(file_data.keys()))
    content = next(iter(file_data.values()))
    
    # Prompt for validation documentation
    prompt = f"""Analyze this code and generate structured documentation in markdown format with the following sections:
    - **Code Structure**: Provide a high-level overview of how the code is organized.
    - **Code Overview**: Describe the general purpose related to validation.
    - **List of Functions**: Provide a numbered list of functions involved in validation.
    - **Explanation of Functions**: For each function, include:
      - Purpose: What the function does for validation.
      - Parameters: List and describe all parameters.
      - Return Values: Describe what the function returns.
      - Example: Provide a code example with expected output.
    Ensure the output focuses on validation aspects. Here is the code to analyze:\n\n{content}"""

    # Call Groq
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful code documentation assistant."},
            {"role": "user", "content": prompt},
        ],
        model="llama-3.3-70b-versatile",
        max_tokens=1500
    )
    ai_response = chat_completion.choices[0].message.content
    
    return render_template('validation_documentation.html', result=ai_response, filename=filename)