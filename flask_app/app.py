from flask import Flask, request, render_template
from groq import Groq

app = Flask(__name__)

# Your Groq API key here
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Handle file upload
        if 'file' not in request.files:
            return "No file uploaded!", 400
        file = request.files['file']
        if file.filename == '':
            return "No file selected!", 400
        
        # Read file content
        try:
            content = file.read().decode('utf-8')
        except UnicodeDecodeError:
            return "Error: File must be text (e.g., .py, .txt)!", 400
        
        # Get prompt type from radio buttons
        output_type = request.form.get('output_type', 'guide')  # Match form name
        
        # Choose prompt based on type
        if output_type == 'diagram':
           prompt = f"Generate a valid Mermaid flowchart (graph TD syntax) showing the function call structure of this code. Include only function nodes (e.g., main, validate_input) in brackets like A[main]. Use edges like A -->|calls| B[validate_input] with simple labels (e.g., 'calls') without quotes, '>', conditionals (e.g., true, false), or loops. Avoid non-function nodes like 'if __name__'. Example for a code with functions foo and bar: graph TD\n    A[foo] -->|calls| B[bar]\nOutput only the Mermaid code, no explanations:\n\n{content}"
        else:
            prompt = f"Analyze this code and generate a simple setup guide:\n\n{content}"
        
        # Prompt Groq
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful code documentation assistant."},
                {"role": "user", "content": prompt},
            ],
            model="llama-3.3-70b-versatile",
            max_tokens=500
        )
        ai_response = chat_completion.choices[0].message.content
        
        return render_template('index.html', result=ai_response, filename=file.filename, output_type=output_type)
    
    # Show form on GET
    return render_template('index.html', output_type='guide')  # Default for GET

if __name__ == '__main__':
    app.run(debug=True)