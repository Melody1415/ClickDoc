from flask import Flask, request, render_template, redirect, url_for, session
from dashboard import bp_dashboard
from generate import generate
from validation import validation  # New import
from relationship import relationship 

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace with a secure random key later
app.register_blueprint(bp_dashboard)
app.register_blueprint(generate)
app.register_blueprint(validation)
app.register_blueprint(relationship)

@app.route('/', methods=['GET', 'POST'])
def upload():
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
        
        # Store file in session
        session['file'] = {file.filename: content}
        print(session['file'])

        # Redirect to dashboard
        return redirect(url_for('dashboard.dashboard'))  # Use blueprint name + endpoint
    
    # Show upload form on GET
    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)