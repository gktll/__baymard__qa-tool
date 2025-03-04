import streamlit as st
import pandas as pd
from utils.session_manager import load_csv
from utils.helpers import get_judgment_color
from urllib.parse import urlparse
import requests
from PIL import Image
from io import BytesIO

def is_valid_image_url(url):
    """Validate if URL is accessible and returns an image"""
    try:
        # Check if URL is well-formed
        result = urlparse(url.strip())
        if not all([result.scheme, result.netloc]):
            return False
            
        # Try to fetch headers only first
        response = requests.head(url.strip(), timeout=5)
        content_type = response.headers.get('content-type', '')
        return 'image' in content_type.lower()
    except:
        return False

def load_and_display_image(url, use_container_width=True, width=None):
    """Safely load and display an image from URL"""
    try:
        response = requests.get(url.strip(), timeout=5)
        image = Image.open(BytesIO(response.content))
        if width:
            st.image(image, width=width)
        else:
            st.image(image, use_container_width=use_container_width)
        return True
    except Exception as e:
        st.warning(f"Could not load image: {url}")
        return False


def render_guideline_detail(citation_code):
    if not citation_code:
        return
    
    def init_styles():
        return st.markdown("""
            <style>
            .title {font-size:20px}
            .text {font-size:16px}
            .section-heading {font-size:18px; font-weight:bold; margin:12px 0}
            .card {padding:1rem; border-radius:8px; margin:1.5rem 0}
            </style>
        """, unsafe_allow_html=True)

    init_styles()
    df = load_csv(st.session_state.uploaded_file)
    guideline = df[df['Citation Code: Platform-Specific'] == citation_code].iloc[0]
    
    col1, col2 = st.columns([6, 4])
    
    with col1:
        st.markdown(f'<p class="text"><strong>Case Study:</strong> {guideline["Case Study Title"].lower()}</p>', 
                   unsafe_allow_html=True)
        st.markdown(f'<h1 class="title">{citation_code} - {guideline["Title"]}</h1>', 
                   unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="card" style="background-color:{get_judgment_color(guideline['Judgement'])}; color:white; text-align:center">
            <strong>Judgment:</strong> {guideline['Judgement']}
        </div>
        """, unsafe_allow_html=True)

        st.write("###")
        sections = [
            ("Scenario", "Scenarios"),
            ("Customer Facing Notes", "Client-Facing Comment")
        ]
        
        for heading, field in sections:
            st.markdown(f'<h3 class="section-heading">{heading}</h3>', unsafe_allow_html=True)
            content = guideline[field] if pd.notna(guideline[field]) else "None"
            st.markdown(f'<p class="text">{content}</p>', unsafe_allow_html=True)

        st.write("###")
        with st.expander("Issue & Recommendation"):
            st.subheader("Issue Description")
            st.write(guideline['Issue'])
            st.subheader("Recommendation")
            st.write(guideline['Advice'])

        with st.expander("Mastertext"):
            st.write(guideline['Master Text(s)'])

    with col2:
        # Handle images with proper validation and error handling
        if pd.notna(guideline['Image URLs']):
            image_urls = [url.strip() for url in guideline['Image URLs'].split(',') if url.strip()]
            valid_image_urls = [url for url in image_urls if is_valid_image_url(url)]
            
            if valid_image_urls:
                # Display main image
                load_and_display_image(valid_image_urls[0])
                
                # Display thumbnails if there are more images
                if len(valid_image_urls) > 1:
                    st.write("Additional Images:")
                    num_cols = min(4, len(valid_image_urls[1:]))
                    if num_cols > 0:
                        thumbnail_cols = st.columns(num_cols)
                        for i, img_url in enumerate(valid_image_urls[1:num_cols + 1]):
                            with thumbnail_cols[i]:
                                load_and_display_image(img_url, use_container_width=False, width=60)
            else:
                st.info("No valid images available for this guideline.")

        st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)
        with st.expander("Additional Information", expanded=True):
            st.markdown(f'<p class="medium-font"><strong>Theme:</strong> {guideline["Catalog Theme Title"]}</p>', 
                       unsafe_allow_html=True)
            st.markdown(f'<p class="medium-font"><strong>Topic:</strong> {guideline["Catalog Topic Title"]}</p>', 
                       unsafe_allow_html=True)
            if pd.notna(guideline['Gemini URL']):
                st.markdown(f"[View in Gemini]({guideline['Gemini URL']})")

    st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)
    if st.button("← Back to Overview"):
        st.session_state.selected_guideline = None
        st.rerun()


