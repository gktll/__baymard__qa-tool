# # pages/render_guideline_detail.py

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


# def render_guideline_detail(citation_code):
#     if not citation_code:
#         return
    
#     def init_styles():
#         return st.markdown("""
#             <style>
#             .title {font-size:20px}
#             .text {font-size:16px}
#             .section-heading {font-size:18px; font-weight:bold; margin:12px 0}
#             .card {padding:1rem; border-radius:8px; margin:1.5rem 0}
#             </style>
#         """, unsafe_allow_html=True)

#     init_styles()
#     df = load_csv(st.session_state.uploaded_file)
#     guideline = df[df['Citation Code: Platform-Specific'] == citation_code].iloc[0]
    
#     col1, col2 = st.columns([6, 4])
    
#     with col1:
#         st.markdown(f'<p class="text"><strong>Case Study:</strong> {guideline["Case Study Title"].lower()}</p>', 
#                    unsafe_allow_html=True)
#         st.markdown(f'<h1 class="title">{citation_code} - {guideline["Title"]}</h1>', 
#                    unsafe_allow_html=True)
        
#         st.markdown(f"""
#         <div class="card" style="background-color:{get_judgment_color(guideline['Judgement'])}; color:white; text-align:center">
#             <strong>Judgment:</strong> {guideline['Judgement']}
#         </div>
#         """, unsafe_allow_html=True)

#         st.write("###")
#         sections = [
#             ("Scenario", "Scenarios"),
#             ("Customer Facing Notes", "Client-Facing Comment")
#         ]
        
#         for heading, field in sections:
#             st.markdown(f'<h3 class="section-heading">{heading}</h3>', unsafe_allow_html=True)
#             content = guideline[field] if pd.notna(guideline[field]) else "None"
#             st.markdown(f'<p class="text">{content}</p>', unsafe_allow_html=True)

#         st.write("###")
#         with st.expander("Issue & Recommendation"):
#              st.subheader("Issue Description")
#              st.write(guideline['Issue'])
#              st.subheader("Recommendation")
#              st.write(guideline['Advice'])

#         with st.expander("Mastertext"):
#              st.write(guideline['Master Text(s)'])

#     with col2:
#         # Handle images with proper validation and error handling
#         if pd.notna(guideline['Image URLs']):
#             image_urls = [url.strip() for url in guideline['Image URLs'].split(',') if url.strip()]
#             valid_image_urls = [url for url in image_urls if is_valid_image_url(url)]
            
#             if valid_image_urls:
#                 # Display main image
#                 load_and_display_image(valid_image_urls[0])
                
#                 # Display thumbnails if there are more images
#                 if len(valid_image_urls) > 1:
#                     st.write("Additional Images:")
#                     num_cols = min(4, len(valid_image_urls[1:]))
#                     if num_cols > 0:
#                         thumbnail_cols = st.columns(num_cols)
#                         for i, img_url in enumerate(valid_image_urls[1:num_cols + 1]):
#                             with thumbnail_cols[i]:
#                                 load_and_display_image(img_url, use_container_width=False, width=60)
#             else:
#                 st.info("No valid images available for this guideline.")

#         st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)
#         with st.expander("Additional Information", expanded=True):
#             st.markdown(f'<p class="medium-font"><strong>Theme:</strong> {guideline["Catalog Theme Title"]}</p>', 
#                        unsafe_allow_html=True)
#             st.markdown(f'<p class="medium-font"><strong>Topic:</strong> {guideline["Catalog Topic Title"]}</p>', 
#                        unsafe_allow_html=True)
#             if pd.notna(guideline['Gemini URL']):
#                 st.markdown(f"[View in Gemini]({guideline['Gemini URL']})")

#     st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)
#     if st.button("← Back to Overview"):
#         st.session_state.selected_guideline = None
#         st.rerun()


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
            .thumbnail-container {
                cursor: pointer;
                transition: transform 0.2s;
                border: 2px solid transparent;
            }
            .thumbnail-container:hover {
                transform: scale(1.05);
                border: 2px solid #4b8bf4;
            }
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
        # Initialize session state for selected image if not present
        if 'selected_image_index' not in st.session_state:
            st.session_state.selected_image_index = 0
            
        # Handle images with proper validation and error handling
        if pd.notna(guideline['Image URLs']):
            # Split the image URLs and ensure they're strings
            image_urls_raw = guideline['Image URLs']
            
            # Handle different formats of Image URLs (string, list, etc.)
            if isinstance(image_urls_raw, str):
                # Split by commas if it's a string
                image_urls = [url.strip() for url in image_urls_raw.split(',') if url.strip()]
            elif isinstance(image_urls_raw, list):
                # Already a list, just ensure all items are strings
                image_urls = [str(url).strip() for url in image_urls_raw if str(url).strip()]
            else:
                # Single item that's not a string
                image_urls = [str(image_urls_raw).strip()] if str(image_urls_raw).strip() else []
            
            # Validate each URL
            valid_image_urls = []
            invalid_urls = []
            
            for url in image_urls:
                if is_valid_image_url(url):
                    valid_image_urls.append(url)
                else:
                    invalid_urls.append(url)
            
            # Only show invalid URL warnings in an expander to keep the UI clean
            if invalid_urls:
                with st.expander("Image Loading Issues"):
                    for url in invalid_urls:
                        st.warning(f"Could not load image: {url[:50]}...")
            
            # Display the images if we have valid URLs
            if valid_image_urls:
                # If an image is clicked, update the selected index
                if 'clicked_image' in st.session_state and st.session_state.clicked_image is not None:
                    st.session_state.selected_image_index = st.session_state.clicked_image
                    st.session_state.clicked_image = None  # Reset after use
                
                # Ensure the index is valid (in case the number of images changed)
                if st.session_state.selected_image_index >= len(valid_image_urls):
                    st.session_state.selected_image_index = 0
                
                # Display the main image (selected one)
                main_image_url = valid_image_urls[st.session_state.selected_image_index]
                load_and_display_image(main_image_url)
                
                # Display thumbnails of all images
                if len(valid_image_urls) > 1:
                    st.write("##### All Images:")
                    
                    # Determine number of columns based on image count
                    cols_per_row = min(4, len(valid_image_urls))
                    cols = st.columns(cols_per_row)
                    
                    # Display thumbnails with highlight for selected one
                    for i, url in enumerate(valid_image_urls):
                        with cols[i % cols_per_row]:
                            # Add border to currently selected thumbnail
                            border = "3px solid #4b8bf4" if i == st.session_state.selected_image_index else "1px solid gray"
                            st.markdown(f'<div style="border:{border}; padding:2px;">', unsafe_allow_html=True)
                            
                            # We'll use a button with an image inside for each thumbnail
                            if st.button(f"Image {i+1}", key=f"thumb_{i}"):
                                st.session_state.selected_image_index = i
                                st.rerun()
                                
                            # Show a small preview
                            try:
                                response = requests.get(url.strip(), timeout=3)
                                img = Image.open(BytesIO(response.content))
                                st.image(img, width=60)
                            except:
                                st.write("❌")
                                
                            st.markdown('</div>', unsafe_allow_html=True)
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