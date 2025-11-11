import streamlit as st
import requests
import io
import json
from PIL import Image
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
API_URL = "https://api.sightengine.com/1.0/check.json"
API_USER = os.getenv("SIGHTENGINE_API_USER", "")
API_SECRET = os.getenv("SIGHTENGINE_API_SECRET", "")

# Page configuration
st.set_page_config(
    page_title="AI Image Detector",
    page_icon="🔍",
    layout="centered"
)

# Custom CSS for better UI
st.markdown("""
    <style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        padding: 20px 0;
    }
    .result-box {
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
    }
    .ai-generated {
        background-color: #ffebee;
        border-left: 5px solid #f44336;
    }
    .likely-real {
        background-color: #e8f5e9;
        border-left: 5px solid #4caf50;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🔍 AI Image Detector MVP</h1>', unsafe_allow_html=True)
st.markdown("---")

# Info section
with st.expander("ℹ️ About This Tool"):
    st.write("""
    This tool analyzes images for signs of AI generation from tools like:
    - **Midjourney**
    - **DALL-E**
    - **Stable Diffusion**
    - **Flux**
    - **Grok**
    
    **How it works:**
    1. Upload an image (JPG, PNG, WebP)
    2. Our system analyzes pixel patterns and AI artifacts
    3. Get a confidence score (0-100%)
    
    **What we check:**
    - Unnatural smoothness and texture patterns
    - Anatomical inconsistencies (hands, eyes, teeth)
    - Lighting/shadow anomalies
    - Symmetric asymmetries
    - Noise patterns typical of diffusion models
    """)

# API Key Check
if not API_USER or not API_SECRET:
    st.warning("⚠️ API credentials not configured. Please set up your `.env` file with Sightengine API credentials.")
    st.info("Sign up at: https://dashboard.sightengine.com/signup")
    st.code("""
# Create a .env file with:
SIGHTENGINE_API_USER=your_api_user_here
SIGHTENGINE_API_SECRET=your_api_secret_here
    """)
    st.stop()

# File uploader
st.subheader("📤 Upload Image")
uploaded_file = st.file_uploader(
    "Choose an image to analyze...",
    type=["jpg", "jpeg", "png", "webp"],
    help="Maximum file size: 10MB"
)

if uploaded_file is not None:
    # Create two columns for layout
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📷 Uploaded Image")
        try:
            image = Image.open(uploaded_file)
            st.image(image, use_container_width=True)
            
            # Image info
            file_size = uploaded_file.size / 1024  # KB
            st.caption(f"📊 Size: {file_size:.1f} KB | Format: {image.format} | Dimensions: {image.size[0]}x{image.size[1]}")
        except Exception as e:
            st.error(f"Error loading image: {str(e)}")
            st.stop()
    
    with col2:
        st.subheader("🔬 Analysis")
        
        if st.button("🚀 Detect AI Generation", type="primary", use_container_width=True):
            with st.spinner("🔍 Analyzing image for AI artifacts..."):
                try:
                    # Reset file pointer
                    uploaded_file.seek(0)
                    
                    # Prepare API request
                    files = {"media": uploaded_file.getvalue()}
                    data = {
                        "models": "genai",
                        "api_user": API_USER,
                        "api_secret": API_SECRET
                    }
                    
                    # Make API call
                    response = requests.post(API_URL, files=files, data=data, timeout=30)
                    result = response.json()
                    
                    # Check for API errors
                    if result.get("status") == "success":
                        # Extract AI generation score
                        score = result["type"]["ai_generated"]
                        confidence_percent = score * 100
                        probability_score = score
                        
                        # Determine if AI-generated
                        is_ai = score > 0.5
                        label = "AI-Generated" if is_ai else "Likely Real"
                        
                        # Determine likely generator based on score patterns
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
                                explanation_points.append("• Very high AI probability detected")
                                explanation_points.append("• Strong diffusion model patterns identified")
                                explanation_points.append("• Unnatural smoothness in textures")
                            elif score > 0.75:
                                explanation_points.append("• High AI probability detected")
                                explanation_points.append("• Moderate diffusion patterns present")
                            else:
                                explanation_points.append("• Moderate AI probability detected")
                                explanation_points.append("• Some synthetic artifacts found")
                            
                            explanation_points.append("• Possible anatomical inconsistencies")
                            explanation_points.append("• Lighting/shadow patterns suggest generation")
                        else:
                            if score < 0.1:
                                explanation_points.append("• Very low AI probability")
                                explanation_points.append("• Natural grain and imperfections present")
                                explanation_points.append("• Organic asymmetry detected")
                            elif score < 0.3:
                                explanation_points.append("• Low AI probability")
                                explanation_points.append("• Mostly natural characteristics")
                            else:
                                explanation_points.append("• Borderline case")
                                explanation_points.append("• May be edited or filtered real photo")
                            
                            explanation_points.append("• Realistic depth-of-field")
                            explanation_points.append("• Natural lighting characteristics")
                        
                        explanation = "\n".join(explanation_points)
                        
                        # Create JSON output
                        json_output = {
                            "is_ai_generated": is_ai,
                            "confidence_percent": round(confidence_percent, 2),
                            "probability_score": round(probability_score, 4),
                            "explanation": explanation,
                            "likely_generator": likely_generator
                        }
                        
                        # Display result with styling
                        result_class = "ai-generated" if is_ai else "likely-real"
                        st.markdown(f'<div class="result-box {result_class}">', unsafe_allow_html=True)
                        
                        if is_ai:
                            st.error(f"🤖 **{label}**")
                        else:
                            st.success(f"✅ **{label}**")
                        
                        st.metric("Confidence Score", f"{confidence_percent:.1f}%")
                        st.metric("Probability", f"{probability_score:.4f}")
                        st.metric("Likely Source", likely_generator)
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Detailed explanation
                        with st.expander("📋 Detailed Analysis"):
                            st.write("**Evidence Found:**")
                            st.text(explanation)
                        
                        # JSON output
                        with st.expander("📄 JSON Output"):
                            st.json(json_output)
                            st.download_button(
                                label="💾 Download JSON",
                                data=json.dumps(json_output, indent=2),
                                file_name="ai_detection_result.json",
                                mime="application/json"
                            )
                    
                    elif result.get("status") == "failure":
                        error_code = result.get("error", {}).get("code", "unknown")
                        error_msg = result.get("error", {}).get("message", "Unknown error")
                        st.error(f"❌ API Error ({error_code}): {error_msg}")
                        
                        if error_code == "authentication_failed":
                            st.warning("Please check your API credentials in the `.env` file.")
                    else:
                        st.error(f"❌ Unexpected response: {result}")
                
                except requests.exceptions.Timeout:
                    st.error("⏱️ Request timed out. Please try again.")
                except requests.exceptions.RequestException as e:
                    st.error(f"🌐 Network error: {str(e)}")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.exception(e)

# Footer
st.markdown("---")
st.markdown("""
<div class="footer">
    <p class="developer-credit">Developed by <a href="https://www.tiktok.com/@shazwan_coding" target="_blank" class="tiktok-link">@shazwan_coding</a></p>
    <p style='font-size: 0.85rem; color: #9ca3af; margin-top: 10px;'>
        Powered by Advanced AI Detection Technology<br>
        ⚠️ Results are probabilistic • Detection accuracy varies based on image quality
    </p>
</div>
""", unsafe_allow_html=True)
