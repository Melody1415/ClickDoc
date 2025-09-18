from flask import Blueprint, render_template, session, redirect, url_for
from groq import Groq

generate = Blueprint('generate', __name__)

GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

@generate.route('/function_documentation')
def function_documentation():
    file_data = session.get('file', {})
    if not file_data:
        return redirect(url_for('dashboard.dashboard'))  # Back to dashboard if no file
    filename = next(iter(file_data.keys()))
    content = next(iter(file_data.values()))
    
    # Prompt for function documentation
    prompt = f"Analyze this code and generate detailed documentation for each function, including purpose, parameters, and return values. Output in markdown format:\n\n{content}"
    
    # Call Groq
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful code documentation assistant."},
            {"role": "user", "content": prompt},
        ],
        model="llama-3.3-70b-versatile",
        max_tokens=1000
    )
    ai_response = chat_completion.choices[0].message.content
    
    return render_template('function_documentation.html', result=ai_response, filename=filename)