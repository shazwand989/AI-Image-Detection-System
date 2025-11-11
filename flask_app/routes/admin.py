"""
Admin upload routes - File upload handling for manuals, posters, and case images
"""
import os
import time
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from database import execute_query
from routes.auth import admin_required

admin_bp = Blueprint('admin', __name__)

ALLOWED_EXTENSIONS = {
    'pdf': {'pdf'},
    'image': {'png', 'jpg', 'jpeg', 'gif', 'webp', 'avif'}
}

def allowed_file(filename, file_type='image'):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS.get(file_type, set())

@admin_bp.route('/user-manual', methods=['POST'])
@admin_required
def upload_manual(current_user):
    """Upload user manual PDF"""
    if 'manual' not in request.files:
        return jsonify({'message': 'No file provided'}), 400
    
    file = request.files['manual']
    title = request.form.get('title', '')
    
    if not title:
        return jsonify({'message': 'Title is required'}), 400
    
    if file.filename == '':
        return jsonify({'message': 'No file selected'}), 400
    
    if not allowed_file(file.filename, 'pdf'):
        return jsonify({'message': 'Only PDF files allowed'}), 400
    
    # Save file
    filename = secure_filename(file.filename)
    timestamp = str(int(time.time() * 1000))
    filename = f"{timestamp}_{filename}"
    
    manual_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'manuals')
    os.makedirs(manual_dir, exist_ok=True)
    upload_path = os.path.join(manual_dir, filename)
    file.save(upload_path)
    
    # Save to database
    file_path = f"/uploads/manuals/{filename}"
    manual_id = execute_query(
        "INSERT INTO user_manual (title, file_path) VALUES (%s, %s)",
        (title, file_path)
    )
    
    if manual_id:
        return jsonify({
            'message': 'Manual uploaded successfully',
            'id': manual_id,
            'file_path': file_path
        }), 201
    else:
        return jsonify({'message': 'Failed to save manual'}), 500

@admin_bp.route('/scam-tips', methods=['POST'])
@admin_required
def upload_scam_tip(current_user):
    """Upload scam tip poster"""
    if 'poster' not in request.files:
        return jsonify({'message': 'No file provided'}), 400
    
    file = request.files['poster']
    title = request.form.get('title', '')
    
    if not title:
        return jsonify({'message': 'Title is required'}), 400
    
    if file.filename == '':
        return jsonify({'message': 'No file selected'}), 400
    
    if not allowed_file(file.filename, 'image'):
        return jsonify({'message': 'Only image files allowed'}), 400
    
    # Save file
    filename = secure_filename(file.filename)
    timestamp = str(int(time.time() * 1000))
    filename = f"{timestamp}_{filename}"
    
    poster_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'posters')
    os.makedirs(poster_dir, exist_ok=True)
    upload_path = os.path.join(poster_dir, filename)
    file.save(upload_path)
    
    # Save to database
    image_path = f"/uploads/posters/{filename}"
    tip_id = execute_query(
        "INSERT INTO scam_tips (title, image_path) VALUES (%s, %s)",
        (title, image_path)
    )
    
    if tip_id:
        return jsonify({
            'message': 'Scam tip uploaded successfully',
            'id': tip_id,
            'image_path': image_path
        }), 201
    else:
        return jsonify({'message': 'Failed to save scam tip'}), 500

@admin_bp.route('/scam-cases', methods=['POST'])
@admin_required
def upload_scam_case(current_user):
    """Upload Malaysia scam case"""
    if 'caseImage' not in request.files:
        return jsonify({'message': 'No file provided'}), 400
    
    file = request.files['caseImage']
    headline = request.form.get('headline') or request.form.get('title', '')
    news_link = request.form.get('news_link', '')
    
    if not headline:
        return jsonify({'message': 'Headline is required'}), 400
    
    if file.filename == '':
        return jsonify({'message': 'No file selected'}), 400
    
    if not allowed_file(file.filename, 'image'):
        return jsonify({'message': 'Only image files allowed'}), 400
    
    # Save file
    filename = secure_filename(file.filename)
    timestamp = str(int(time.time() * 1000))
    filename = f"{timestamp}_{filename}"
    
    cases_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'cases')
    os.makedirs(cases_dir, exist_ok=True)
    upload_path = os.path.join(cases_dir, filename)
    file.save(upload_path)
    
    # Save to database
    image_path = f"/uploads/cases/{filename}"
    case_id = execute_query(
        "INSERT INTO malaysia_cases (headline, image_path, news_link) VALUES (%s, %s, %s)",
        (headline, image_path, news_link)
    )
    
    if case_id:
        return jsonify({
            'message': 'Scam case uploaded successfully',
            'id': case_id,
            'image_path': image_path
        }), 201
    else:
        return jsonify({'message': 'Failed to save scam case'}), 500

