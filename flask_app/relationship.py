from flask import Blueprint, render_template, session, redirect, url_for
from groq import Groq

relationship = Blueprint('relationship', __name__)

GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

@relationship.route('/relationship_documentation')
def relationship_documentation():
    file_data = session.get('file', {})
    if not file_data:
        return redirect(url_for('dashboard.dashboard'))  # Back to dashboard if no file
    filename = next(iter(file_data.keys()))
    content = next(iter(file_data.values()))
    
    # Prompt for relationship documentation
    prompt = f"""Analyze this code and generate structured documentation in markdown format with the following sections:
    - **Code Structure**: Provide a high-level overview of how the code is organized, focusing on relationships between components.
    - **Code Overview**: Describe the general purpose related to relationships between functions or data.
    - **List of Functions**: Provide a numbered list of functions involved in relationships.
    - **Explanation of Functions**: For each function, include:
      - Purpose: What the function does in terms of relationships.
      - Parameters: List and describe all parameters.
      - Return Values: Describe what the function returns.
      - Example: Provide a code example with expected output.
    Ensure the output focuses on how functions or data interact. Here is the code to analyze:\n\n{content}"""

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
    
    return render_template('relationship_documentation.html', result=ai_response, filename=filename)