from flask import Blueprint, render_template, session,request,jsonify

bp_dashboard = Blueprint('functiondashboard', __name__)


@bp_dashboard.route('/api/set_files', methods=['POST'])
def set_files():
    try:
        data = request.get_json()
        files = data.get('files', [])
        if not files:
            return jsonify({'error': 'No files provided'}), 400
        # Store all files
        session['files'] = files
        return jsonify({'status': 'success', 'file_count': len(files)}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp_dashboard.route('/functiondashboard')
def dashboard():
    files = session.get('files', [])  # Use 'files' key, default to empty list
    return render_template('functiondashboard.html', files=files)  # Pass files list to template