"""
Content management routes - CRUD operations for user manuals, scam tips, and cases
"""
from flask import Blueprint, request, jsonify
from database import execute_query
from routes.auth import token_required, admin_required

content_bp = Blueprint('content', __name__)

# ===== GET ROUTES (Public access) =====

@content_bp.route('/user-manual', methods=['GET'])
def get_user_manuals():
    """Get all user manuals"""
    manuals = execute_query(
        "SELECT id, title, file_path, created_at FROM user_manual ORDER BY created_at DESC",
        fetch_all=True
    )
    return jsonify(manuals or []), 200

@content_bp.route('/scam-tips', methods=['GET'])
def get_scam_tips():
    """Get all scam tips"""
    tips = execute_query(
        "SELECT id, title, image_path, created_at FROM scam_tips ORDER BY created_at DESC",
        fetch_all=True
    )
    return jsonify(tips or []), 200

@content_bp.route('/scam-cases', methods=['GET'])
def get_scam_cases():
    """Get all Malaysia scam cases"""
    cases = execute_query(
        "SELECT id, headline, image_path, news_link, created_at FROM malaysia_cases ORDER BY created_at DESC",
        fetch_all=True
    )
    return jsonify(cases or []), 200

# ===== POST ROUTES (Admin only) =====

@content_bp.route('/user-manual', methods=['POST'])
@admin_required
def create_user_manual(current_user):
    """Create new user manual entry"""
    data = request.get_json()
    
    if not data or not data.get('title'):
        return jsonify({'message': 'Title is required'}), 400
    
    title = data.get('title')
    body = data.get('body', '')
    
    manual_id = execute_query(
        "INSERT INTO user_manual (title, file_path) VALUES (%s, %s)",
        (title, body)
    )
    
    if manual_id:
        return jsonify({'message': 'Manual created', 'id': manual_id}), 201
    else:
        return jsonify({'message': 'Failed to create manual'}), 500

@content_bp.route('/scam-tips', methods=['POST'])
@admin_required
def create_scam_tip(current_user):
    """Create new scam tip entry"""
    data = request.get_json()
    
    if not data or not data.get('title'):
        return jsonify({'message': 'Title is required'}), 400
    
    title = data.get('title')
    body = data.get('body', '')
    
    tip_id = execute_query(
        "INSERT INTO scam_tips (title, image_path) VALUES (%s, %s)",
        (title, body)
    )
    
    if tip_id:
        return jsonify({'message': 'Scam tip created', 'id': tip_id}), 201
    else:
        return jsonify({'message': 'Failed to create scam tip'}), 500

@content_bp.route('/scam-cases', methods=['POST'])
@admin_required
def create_scam_case(current_user):
    """Create new scam case entry"""
    data = request.get_json()
    
    if not data or not data.get('title'):
        return jsonify({'message': 'Title/headline is required'}), 400
    
    title = data.get('title')
    body = data.get('body', '')
    
    case_id = execute_query(
        "INSERT INTO malaysia_cases (headline, image_path, news_link) VALUES (%s, %s, %s)",
        (title, body, '')
    )
    
    if case_id:
        return jsonify({'message': 'Scam case created', 'id': case_id}), 201
    else:
        return jsonify({'message': 'Failed to create scam case'}), 500

# ===== PUT ROUTES (Admin only - Update) =====

@content_bp.route('/<resource>/<int:item_id>', methods=['PUT'])
@admin_required
def update_content(current_user, resource, item_id):
    """Update content item"""
    data = request.get_json()
    
    if not data:
        return jsonify({'message': 'No data provided'}), 400
    
    title = data.get('title')
    body = data.get('body')
    
    if not title or not body:
        return jsonify({'message': 'Title and body required'}), 400
    
    # Map resource to table
    table_map = {
        'user-manual': ('user_manual', 'file_path'),
        'scam-tips': ('scam_tips', 'image_path'),
        'scam-cases': ('malaysia_cases', 'image_path')
    }
    
    if resource not in table_map:
        return jsonify({'message': 'Invalid resource'}), 400
    
    table_name, body_field = table_map[resource]
    
    # For scam-cases, use 'headline' instead of 'title'
    title_field = 'headline' if resource == 'scam-cases' else 'title'
    
    execute_query(
        f"UPDATE {table_name} SET {title_field} = %s, {body_field} = %s WHERE id = %s",
        (title, body, item_id)
    )
    
    return jsonify({'message': 'Updated successfully'}), 200

# ===== DELETE ROUTES (Admin only) =====

@content_bp.route('/<resource>/<int:item_id>', methods=['DELETE'])
@admin_required
def delete_content(current_user, resource, item_id):
    """Delete content item"""
    # Map resource to table
    table_map = {
        'user-manual': 'user_manual',
        'scam-tips': 'scam_tips',
        'scam-cases': 'malaysia_cases'
    }
    
    if resource not in table_map:
        return jsonify({'message': 'Invalid resource'}), 400
    
    table_name = table_map[resource]
    
    execute_query(
        f"DELETE FROM {table_name} WHERE id = %s",
        (item_id,)
    )
    
    return jsonify({'message': 'Deleted successfully'}), 200
