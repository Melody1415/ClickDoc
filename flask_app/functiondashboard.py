from flask import Blueprint, render_template, session,request,jsonify
from dotenv import load_dotenv
import os

bp_dashboard = Blueprint('functiondashboard', __name__)

@bp_dashboard.route('/functiondashboard')
def dashboard():
    files = session.get('files', [])  # Use 'files' key, default to empty list
    return render_template('functiondashboard.html', files=files)  # Pass files list to template