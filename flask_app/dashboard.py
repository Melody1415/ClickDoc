from flask import Blueprint, render_template, session

bp_dashboard = Blueprint('dashboard', __name__)

@bp_dashboard.route('/dashboard')
def dashboard():
    file_data = session.get('file', {})
    return render_template('dashboard.html', file=file_data)