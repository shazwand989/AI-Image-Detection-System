"""
Flask Application Server - AI Image Detection & Content Management
Replaces Node.js Express server with Python Flask
"""
import os
from flask import Flask, render_template, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to Python path
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import blueprints
from routes.auth import auth_bp
from routes.content import content_bp
from routes.admin import admin_bp
from routes.ai_detection import ai_detection_bp
from database import init_db

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-this')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# CORS configuration
CORS(app)

# Create upload directories
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(os.path.join(UPLOAD_FOLDER, 'manuals'), exist_ok=True)
os.makedirs(os.path.join(UPLOAD_FOLDER, 'posters'), exist_ok=True)
os.makedirs(os.path.join(UPLOAD_FOLDER, 'cases'), exist_ok=True)
os.makedirs(os.path.join(UPLOAD_FOLDER, 'images'), exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(content_bp, url_prefix='/api/content')
app.register_blueprint(admin_bp, url_prefix='/api/admin')
app.register_blueprint(ai_detection_bp, url_prefix='/api')

# Serve static files
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Main route - serve index page
@app.route('/')
def index():
    return render_template('index.html')

# Health check
@app.route('/health')
def health():
    return {'status': 'ok'}

if __name__ == '__main__':
    print("🔧 Initializing database...")
    init_db()
    print("✅ Database ready")
    
    PORT = int(os.getenv('PORT', 4000))
    print(f"🚀 Server starting on http://localhost:{PORT}")
    print("Press Ctrl+C to stop")
    
    app.run(
        host='0.0.0.0',
        port=PORT,
        debug=os.getenv('FLASK_ENV') == 'development'
    )
