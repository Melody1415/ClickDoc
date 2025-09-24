from flask import Flask, send_from_directory,request,session,jsonify
from functiondashboard import bp_dashboard
from generate import generate
from validation import validation  # New import
from relationship import relationship 
from setup import setup 
from tech_stack import tech_stack 

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = 'your_secret_key_here'  # Replace with a secure random key later
app.config['SESSION_TYPE'] = 'filesystem'  # Ensure session persistence

app.register_blueprint(bp_dashboard)
app.register_blueprint(generate)
app.register_blueprint(validation)
app.register_blueprint(relationship)
app.register_blueprint(setup)
app.register_blueprint(tech_stack)

# Route for home page (static home.html)
@app.route('/')
def home():
    return send_from_directory('static', 'home.html')

# Route for upload page (static upload.html)
@app.route('/upload')
def serve_upload():
    return send_from_directory('static', 'upload.html')


# Route for team member's dashboard (static team_dashboard.html)
@app.route('/dashboard')
def serve_dashboard():
    return send_from_directory('static', 'dashboard.html')




if __name__ == '__main__':
    app.run(debug=True)