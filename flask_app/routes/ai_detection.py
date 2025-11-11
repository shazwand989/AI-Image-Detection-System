"""
AI Image Detection routes - Using Sightengine API
Replaces reverse image search with AI-generated image detection
"""
import os
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import requests
from datetime import datetime
from database import execute_query
from routes.auth import token_required

ai_detection_bp = Blueprint('ai_detection', __name__)

# Sightengine API Configuration
API_URL = "https://api.sightengine.com/1.0/check.json"
API_USER = os.getenv("SIGHTENGINE_API_USER", "")
API_SECRET = os.getenv("SIGHTENGINE_API_SECRET", "")

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@ai_detection_bp.route('/detect-ai-image', methods=['POST'])
def detect_ai_image():
    """
    Detect if uploaded image is AI-generated
    Replaces the reverse image search functionality
    """
    if 'image' not in request.files:
        return jsonify({'message': 'No image file provided'}), 400
    
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({'message': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'message': 'Invalid file type. Allowed: PNG, JPG, JPEG, WebP'}), 400
    
    # Check API credentials
    if not API_USER or not API_SECRET:
        return jsonify({
            'message': 'API credentials not configured',
            'error': 'Sightengine API credentials missing'
        }), 500
    
    try:
        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{filename}"
        
        upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'images', filename)
        file.save(upload_path)
        
        # Read file for API request
        with open(upload_path, 'rb') as image_file:
            files = {"media": image_file.read()}
        
        # Make API call to Sightengine
        data = {
            "models": "genai",
            "api_user": API_USER,
            "api_secret": API_SECRET
        }
        
        response = requests.post(API_URL, files=files, data=data, timeout=30)
        result = response.json()
        
        # Check for API errors
        if result.get("status") != "success":
            error_code = result.get("error", {}).get("code", "unknown")
            error_msg = result.get("error", {}).get("message", "Unknown error")
            return jsonify({
                'message': f'API Error ({error_code}): {error_msg}',
                'error': error_msg
            }), 400
        
        # Extract AI generation score
        score = result["type"]["ai_generated"]
        confidence_percent = score * 100
        probability_score = score
        
        # Determine if AI-generated
        is_ai = score > 0.5
        
        # Determine likely generator
        if is_ai:
            if score > 0.9:
                likely_generator = "Midjourney/DALL-E (High Confidence)"
            elif score > 0.75:
                likely_generator = "Stable Diffusion/Flux"
            else:
                likely_generator = "Unknown AI Generator"
        else:
            likely_generator = "Real Photo"
        
        # Generate explanation
        explanation_points = []
        if is_ai:
            if score > 0.9:
                explanation_points.extend([
                    "• Very high AI probability detected",
                    "• Strong diffusion model patterns identified",
                    "• Unnatural smoothness in textures"
                ])
            elif score > 0.75:
                explanation_points.extend([
                    "• High AI probability detected",
                    "• Moderate diffusion patterns present"
                ])
            else:
                explanation_points.extend([
                    "• Moderate AI probability detected",
                    "• Some synthetic artifacts found"
                ])
            
            explanation_points.extend([
                "• Possible anatomical inconsistencies",
                "• Lighting/shadow patterns suggest generation"
            ])
        else:
            if score < 0.1:
                explanation_points.extend([
                    "• Very low AI probability",
                    "• Natural grain and imperfections present",
                    "• Organic asymmetry detected"
                ])
            elif score < 0.3:
                explanation_points.extend([
                    "• Low AI probability",
                    "• Mostly natural characteristics"
                ])
            else:
                explanation_points.extend([
                    "• Borderline case",
                    "• May be edited or filtered real photo"
                ])
            
            explanation_points.extend([
                "• Realistic depth-of-field",
                "• Natural lighting characteristics"
            ])
        
        explanation = "\n".join(explanation_points)
        
        # Create response JSON
        detection_result = {
            "is_ai_generated": is_ai,
            "confidence_percent": round(confidence_percent, 2),
            "probability_score": round(probability_score, 4),
            "explanation": explanation,
            "likely_generator": likely_generator,
            "image_path": f"/uploads/images/{filename}",
            "filename": file.filename
        }
        
        # Save detection result to database (optional - requires user to be logged in)
        auth_header = request.headers.get('Authorization', '')
        user_id = None
        
        if auth_header.startswith('Bearer '):
            try:
                import jwt
                token = auth_header.split(' ')[1]
                decoded = jwt.decode(token, os.getenv('SECRET_KEY', 'your-secret-key-change-this'), algorithms=['HS256'])
                user_id = decoded.get('id')
            except:
                pass  # User not logged in or invalid token
        
        # Save to database
        execute_query(
            """INSERT INTO ai_detections 
               (filename, image_path, is_ai_generated, confidence_percent, 
                probability_score, likely_generator, explanation, user_id) 
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            (file.filename, f"/uploads/images/{filename}", is_ai, 
             round(confidence_percent, 2), round(probability_score, 4),
             likely_generator, explanation, user_id)
        )
        
        return jsonify(detection_result), 200
        
    except requests.exceptions.Timeout:
        return jsonify({'message': 'Request timed out. Please try again.'}), 504
    except requests.exceptions.RequestException as e:
        return jsonify({'message': f'Network error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500

@ai_detection_bp.route('/detection-history', methods=['GET'])
@token_required
def get_detection_history(current_user):
    """Get AI detection history for logged-in user"""
    user_id = current_user.get('id')
    
    history = execute_query(
        """SELECT id, filename, image_path, is_ai_generated, 
                  confidence_percent, likely_generator, created_at 
           FROM ai_detections 
           WHERE user_id = %s 
           ORDER BY created_at DESC 
           LIMIT 50""",
        (user_id,),
        fetch_all=True
    )
    
    return jsonify(history or []), 200

@ai_detection_bp.route('/detection/<int:detection_id>', methods=['GET'])
@token_required
def get_detection_detail(current_user, detection_id):
    """Get detailed detection result"""
    user_id = current_user.get('id')
    
    detection = execute_query(
        """SELECT * FROM ai_detections 
           WHERE id = %s AND user_id = %s""",
        (detection_id, user_id),
        fetch_one=True
    )
    
    if not detection:
        return jsonify({'message': 'Detection not found'}), 404
    
    return jsonify(detection), 200
