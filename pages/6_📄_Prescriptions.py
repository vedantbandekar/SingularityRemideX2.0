"""
Remidex - Prescriptions Page
Capture and manage prescription images
"""

import streamlit as st
import sys
import os
from datetime import datetime
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.styling import inject_css, render_sidebar_header, render_footer

# Page configuration
st.set_page_config(
    page_title="Prescriptions | Remidex",
    page_icon="📄",
    layout="wide"
)

# Inject premium CSS
inject_css(st)

# Additional page-specific CSS
st.markdown("""
<style>
    .gallery-card {
        background: var(--glass-bg);
        border: 1px solid var(--glass-border);
        border-radius: 16px;
        padding: 1rem;
        margin-bottom: 3rem;
        transition: all 0.3s ease;
    }
    
    .gallery-card:hover {
        border-color: var(--primary-light);
        transform: translateY(-3px);
    }
    
    .img-caption {
        margin-top: 0.5rem;
        font-size: 0.9rem;
        color: var(--text-secondary);
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Ensure directory exists
UPLOAD_DIR = "captured_prescriptions"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Sidebar
render_sidebar_header(st)

st.sidebar.markdown("### 📝 Notes")
st.sidebar.info("Use good lighting when capturing prescriptions for better readability.")

# Main content
st.markdown('<h1 class="page-header">📄 RX Scanner</h1>', unsafe_allow_html=True)
st.markdown('<p class="page-subtitle">Capture and store your digital prescriptions</p>', unsafe_allow_html=True)
st.markdown("---")

# SECTION 1: CAPTURE
st.markdown('<p class="section-title">📸 Capture New Prescription</p>', unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("##### 1. Scan using Camera")
        img_file_buffer = st.camera_input("Take a photo")
    
    with col2:
        st.markdown("##### 2. Preview & Save")
        if img_file_buffer is not None:
            # To read image file buffer as image:
            img = Image.open(img_file_buffer)
            
            # Additional input: Doctor Name / Date
            doc_name = st.text_input("Doctor Name (Optional)", placeholder="Dr. Smith")
            
            if st.button("💾 Save to Gallery", type="primary", use_container_width=True):
                # Generate filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"RX_{timestamp}"
                if doc_name:
                    filename += f"_{doc_name.replace(' ', '_')}"
                filename += ".jpg"
                
                # Save
                save_path = os.path.join(UPLOAD_DIR, filename)
                img.save(save_path)
                
                st.success(f"✅ Saved as {filename}")
                st.rerun()
        else:
            st.info("Waiting for camera input...")
            
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# SECTION 2: GALLERY
st.markdown('<p class="section-title">📂 Your Prescriptions</p>', unsafe_allow_html=True)

# List files
try:
    files = [f for f in os.listdir(UPLOAD_DIR) if f.endswith(('.png', '.jpg', '.jpeg'))]
    files.sort(reverse=True) # Newest first
except Exception as e:
    st.error(f"Error accessing storage: {e}")
    files = []

if not files:
    st.markdown("""
    <div class="info-box">
        📭 No prescriptions saved yet. Use the camera above to scan one.
    </div>
    """, unsafe_allow_html=True)
else:
    # Grid layout
    cols = st.columns(3) # 3 columns for gallery
    
    for idx, file in enumerate(files):
        with cols[idx % 3]:
            file_path = os.path.join(UPLOAD_DIR, file)
            image = Image.open(file_path)
            
            st.markdown('<div class="gallery-card">', unsafe_allow_html=True)
            st.image(image, use_container_width=True)
            
            # Meta info from filename
            # Filename format: RX_YYYYMMDD_HHMMSS_DocName.jpg
            try:
                parts = file.split('_')
                date_str = f"{parts[1][6:]}/{parts[1][4:6]}/{parts[1][:4]}"
                meta_text = f"📅 {date_str}"
                if len(parts) > 3:
                     doc = parts[3].split('.')[0].replace('_', ' ')
                     meta_text += f" | 👨‍⚕️ {doc}"
            except:
                meta_text = file
            
            st.markdown(f'<div class="img-caption">{meta_text}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            if st.button(f"🗑️ Delete", key=f"del_{file}", type="secondary", use_container_width=True):
                os.remove(file_path)
                st.rerun()

render_footer(st)
