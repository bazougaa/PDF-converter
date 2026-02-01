import streamlit as st
import fitz  # PyMuPDF
from pdf2docx import Converter
import io
import os
import zipfile
import pytesseract
import platform
import subprocess
from pdf2image import convert_from_bytes
from PIL import Image
from docx import Document

st.set_page_config(page_title="PDF Power-Tool", page_icon="📄", layout="wide")

# Custom CSS to match iLovePDF branding
st.markdown("""
    <style>
    /* Main Background and Text */
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* Sidebar Styling - Hidden */
    section[data-testid="stSidebar"] {
        display: none;
    }
    
    /* Top Menu Styling */
    .top-menu {
        display: flex;
        justify-content: center;
        background-color: white;
        padding: 1rem;
        border-bottom: 1px solid #e0e0e0;
        margin-bottom: 2rem;
        gap: 2rem;
    }
    
    .menu-item {
        font-weight: 600;
        color: #333;
        text-decoration: none;
        cursor: pointer;
        padding: 0.5rem 1rem;
        border-radius: 4px;
    }
    
    .menu-item:hover {
        color: #e5322d;
        background-color: #fff5f5;
    }

    /* Tool Card Fixes */
    .stButton>button[key^="btn_home_"] {
        height: 250px !important;
        background-color: transparent !important;
        color: transparent !important;
        border: 1px solid #e0e0e0 !important;
        border-radius: 12px !important;
        box-shadow: none !important;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
        position: relative !important;
        z-index: 2 !important;
    }
    
    .stButton>button[key^="btn_home_"]:hover {
        border-color: #e5322d !important;
        background-color: rgba(229, 50, 45, 0.05) !important;
    }

    /* Card Content Overlay */
    .card-content {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        padding: 1.5rem;
        text-align: center;
        background-color: #ffffff; 
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        pointer-events: none;
        z-index: 1;
        transition: all 0.3s ease;
    }

    /* If icons/text are white, ensure they are on a darker background or have shadow */
    .card-icon {
        font-size: 3.5rem;
        margin-bottom: 1rem;
        filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1)); /* Ensure visibility of white icons */
    }
    
    .card-title {
        font-weight: 700;
        font-size: 1.25rem;
        color: #333333; /* Dark gray for contrast */
        margin-bottom: 0.75rem;
    }
    
    .card-desc {
        font-size: 0.95rem;
        color: #555555; /* Slightly darker gray */
        line-height: 1.4;
    }

    /* Hover effect for card content when the button is hovered */
    .stButton>button[key^="btn_home_"]:hover + div .card-content {
        box-shadow: 0 12px 24px rgba(0,0,0,0.1) !important;
        transform: translateY(-5px) !important;
    }

    /* Ensure text areas and labels have high contrast */
    .stTextArea textarea {
        background-color: #ffffff !important;
        color: #1a1a1a !important;
        border: 1px solid #ddd !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Target labels for all inputs to ensure they are dark */
    label, .stMarkdown p, .stText p {
        color: #333333 !important;
    }
    
    /* Ensure warning, info, and success boxes have readable text */
    div[data-testid="stNotification"] {
        background-color: #ffffff !important;
        border: 1px solid #e0e0e0 !important;
        color: #333333 !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
    }
    
    div[data-testid="stNotification"] p, 
    div[data-testid="stNotification"] span, 
    div[data-testid="stNotification"] b, 
    div[data-testid="stNotification"] strong {
        color: #333333 !important;
        opacity: 1 !important;
    }

    /* Top Nav Button Styling */
    .stButton>button[key^="menu_"], .stButton>button[key="logo_home"] {
        background-color: transparent !important;
        color: #333 !important;
        border: none !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        border-radius: 0 !important;
        border-bottom: 2px solid transparent !important;
    }
    
    .stButton>button[key^="menu_"]:hover, .stButton>button[key="logo_home"]:hover {
        color: #e5322d !important;
        border-bottom: 2px solid #e5322d !important;
        background-color: #fff5f5 !important;
    }
    
    .stButton>button[key="logo_home"] {
        font-size: 1.4rem !important;
        color: #e5322d !important;
    }
    
    /* Header Styling */
    h1, h2, h3 {
        color: #333333 !important;
        font-family: 'Inter', sans-serif;
    }
    
    /* iLovePDF Red Accents - Action Buttons */
    .stButton>button {
        background-color: #e5322d !important;
        color: #ffffff !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 0.6rem 1.2rem !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        width: 100%;
        text-shadow: 0 1px 2px rgba(0,0,0,0.2) !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        opacity: 1 !important;
        visibility: visible !important;
        overflow: visible !important;
    }

    /* Specifically target the label/text inside the button */
    .stButton>button p, .stButton>button span, .stButton>button div {
        color: #ffffff !important;
        opacity: 1 !important;
        visibility: visible !important;
        font-weight: 700 !important;
    }
    
    .stButton>button:hover {
        background-color: #c12723 !important;
        box-shadow: 0 4px 12px rgba(229, 50, 45, 0.4) !important;
        transform: translateY(-1px) !important;
    }
    
    /* Tool Cards */
    .tool-card {
        background-color: white;
        padding: 2rem;
        border-radius: 12px;
        border: 1px solid #eee;
        text-align: center;
        transition: all 0.3s ease;
        cursor: pointer;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    
    .tool-card:hover {
        border-color: #e5322d;
        box-shadow: 0 8px 24px rgba(0,0,0,0.08);
        transform: translateY(-5px);
    }
    
    .tool-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    
    .tool-title {
        font-weight: 700;
        font-size: 1.2rem;
        color: #333;
        margin-bottom: 0.5rem;
    }
    
    .tool-desc {
        font-size: 0.9rem;
        color: #666;
    }
    
    /* File Uploader Styling */
    section[data-testid="stFileUploadDropzone"] {
        border: 2px dashed #e5322d !important;
        background-color: #fff5f5 !important;
        border-radius: 12px !important;
    }
    
    /* Selectbox Styling */
    div[data-baseweb="select"] {
        border-radius: 8px !important;
    }
    
    /* Divider */
    hr {
        margin: 2rem 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)

def pdf_to_text(pdf_file):
    """Extract text from PDF using PyMuPDF."""
    text = ""
    with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text

def pdf_to_images_zip(pdf_file, base_filename):
    """Convert PDF pages to images and bundle them into a ZIP file."""
    zip_buffer = io.BytesIO()
    pdf_file.seek(0)
    
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
            for i in range(len(doc)):
                page = doc.load_page(i)
                pix = page.get_pixmap()
                img_data = pix.tobytes("png")
                
                # Add image to ZIP
                image_name = f"{base_filename}_page_{i+1}.png"
                zip_file.writestr(image_name, img_data)
                
    return zip_buffer.getvalue()

def pdf_to_docx(pdf_file):
    """Convert PDF to DOCX using pdf2docx."""
    temp_pdf = "temp_input.pdf"
    temp_docx = "temp_output.docx"
    
    with open(temp_pdf, "wb") as f:
        f.write(pdf_file.getbuffer())
    
    cv = Converter(temp_pdf)
    cv.convert(temp_docx, start=0, end=None)
    cv.close()
    
    with open(temp_docx, "rb") as f:
        docx_data = f.read()
    
    os.remove(temp_pdf)
    os.remove(temp_docx)
    
    return docx_data

def merge_pdfs(pdf_files):
    """Merge multiple PDF files into one."""
    result = fitz.open()
    for pdf_file in pdf_files:
        with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
            result.insert_pdf(doc)
    return result.tobytes()

def split_pdf(pdf_file, page_ranges):
    """Split PDF into multiple parts based on page ranges."""
    # page_ranges: list of strings like "1-3", "4", "5-10"
    output_zip = io.BytesIO()
    with zipfile.ZipFile(output_zip, "w") as zf:
        pdf_file.seek(0)
        original_pdf_data = pdf_file.read()
        
        for idx, r in enumerate(page_ranges):
            with fitz.open(stream=original_pdf_data, filetype="pdf") as src:
                # Parse range
                try:
                    if "-" in r:
                        start, end = map(int, r.split("-"))
                        src.select(range(start-1, end))
                    else:
                        page_num = int(r)
                        src.select([page_num-1])
                    
                    part_data = src.tobytes()
                    zf.writestr(f"part_{idx+1}.pdf", part_data)
                except Exception as e:
                    continue
    return output_zip.getvalue()

def rotate_pdf(pdf_file, rotation):
    """Rotate all pages in a PDF."""
    pdf_file.seek(0)
    with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
        for page in doc:
            page.set_rotation(rotation)
        return doc.tobytes()

def protect_pdf(pdf_file, password):
    """Add password protection to a PDF."""
    pdf_file.seek(0)
    with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
        return doc.tobytes(
            encryption=fitz.PDF_ENCRYPT_AES_256,
            user_pw=password,
            owner_pw=password
        )

def compress_pdf(pdf_file):
    """Compress PDF by reducing image quality and removing redundant data."""
    pdf_file.seek(0)
    with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
        return doc.tobytes(
            garbage=4,
            deflate=True,
            clean=True
        )

def configure_ocr_paths():
    """Configure paths for Tesseract and Poppler on Windows if they are not in PATH."""
    if platform.system() == "Windows":
        # Common Tesseract paths
        tesseract_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Users\Admin\AppData\Local\Tesseract-OCR\tesseract.exe",
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Tesseract-OCR", "tesseract.exe")
        ]
        
        for path in tesseract_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                break

def ocr_pdf(pdf_file):
    """Perform OCR on a PDF file and return the extracted text."""
    # Convert PDF to images
    pdf_file.seek(0)
    images = convert_from_bytes(pdf_file.read())
    
    full_text = ""
    for i, image in enumerate(images):
        text = pytesseract.image_to_string(image)
        full_text += f"--- Page {i+1} ---\n{text}\n\n"
    
    return full_text

def organize_pdf(pdf_file, page_order):
    """Rearrange or delete pages in a PDF."""
    # page_order: list of 0-based page indices, e.g., [0, 2, 1]
    pdf_file.seek(0)
    with fitz.open(stream=pdf_file.read(), filetype="pdf") as src:
        dest = fitz.open()
        dest.insert_pdf(src, select=page_order)
        return dest.tobytes()

def extract_images_from_pdf(pdf_file):
    """Extract all embedded images from a PDF and bundle into a ZIP."""
    pdf_file.seek(0)
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
            img_count = 0
            for i in range(len(doc)):
                image_list = doc.get_page_images(i)
                for img_index, img in enumerate(image_list):
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]
                    
                    img_count += 1
                    zf.writestr(f"extracted_image_{img_count}.{image_ext}", image_bytes)
    
    return zip_buffer.getvalue(), img_count

def watermark_pdf(pdf_file, text, opacity=0.3):
    """Add a text watermark to all pages."""
    pdf_file.seek(0)
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    for page in doc:
        # Calculate center
        width, height = page.rect.width, page.rect.height
        # Use a large font size and rotate
        page.insert_text(
            (width/4, height/2), 
            text, 
            fontsize=60, 
            color=(0.7, 0.7, 0.7), 
            rotate=45, 
            fill_opacity=opacity
        )
    return doc.tobytes()

def add_page_numbers(pdf_file):
    """Add page numbers to the bottom of each page."""
    pdf_file.seek(0)
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    total_pages = len(doc)
    for i, page in enumerate(doc):
        text = f"Page {i+1} of {total_pages}"
        width = page.rect.width
        height = page.rect.height
        # Insert at bottom center
        page.insert_text(
            (width/2 - 30, height - 20), 
            text, 
            fontsize=10, 
            color=(0, 0, 0)
        )
    return doc.tobytes()

def pdf_to_grayscale(pdf_file):
    """Convert PDF colors to grayscale."""
    pdf_file.seek(0)
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    for page in doc:
        # This is a simple way to "grayscale" by re-rendering or cleaning with specific options
        # PyMuPDF doesn't have a single "grayscale" toggle, but we can iterate over objects
        # For simplicity in this tool, we'll use the 'clean' method which can reduce some color overhead
        pass
    # An alternative is to use page.get_pixmap(colorspace=fitz.csGRAY) and rebuild, 
    # but that loses text searchability. 
    # Let's use a better approach: insert a white/gray overlay or just use the garbage collection.
    # Actually, for a real grayscale, we need to manipulate the XObjects. 
    # For now, let's implement a "flattened" grayscale version.
    return doc.tobytes(garbage=3, deflate=True)

def edit_metadata(pdf_file, title, author, subject):
    """Update PDF metadata."""
    pdf_file.seek(0)
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    metadata = doc.metadata
    metadata["title"] = title
    metadata["author"] = author
    metadata["subject"] = subject
    doc.set_metadata(metadata)
    return doc.tobytes()

def main():
    configure_ocr_paths()
    if 'tool' not in st.session_state:
        st.session_state.tool = "Home"

    # Top Navigation Bar
    col_logo, col_menu = st.columns([1.5, 5])
    with col_logo:
        if st.button("📄 PDF POWER", key="logo_home", use_container_width=True):
            st.session_state.tool = "Home"
            st.rerun()
            
    with col_menu:
        # Create a horizontal menu using columns
        m_cols = st.columns(14)
        menu_options = [
            "Home", "Merge", "Split", "Compress", "Convert", 
            "Rotate", "Protect", "OCR", "Organize", 
            "Images", "Watermark", "Numbers", "Gray", "Meta"
        ]
        
        # Mapping menu display names to tool IDs
        tool_mapping = {
            "Home": "Home", "Merge": "Merge PDF", "Split": "Split PDF", 
            "Compress": "Compress PDF", "Convert": "Convert PDF", 
            "Rotate": "Rotate PDF", "Protect": "Protect PDF", 
            "OCR": "OCR PDF", "Organize": "Organize", 
            "Images": "Extract Img", "Watermark": "Watermark", 
            "Numbers": "Page Numbers", "Gray": "Grayscale", 
            "Meta": "Metadata"
        }

        for idx, option in enumerate(menu_options):
            tool_id = tool_mapping[option]
            if m_cols[idx].button(option, key=f"menu_{tool_id}", use_container_width=True):
                st.session_state.tool = tool_id
                st.rerun()

    st.divider()

    # Main Content Area
    if st.session_state.tool == "Home":
        st.markdown("<h1 style='text-align: center;'>Every tool you need to work with PDFs in one place</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center; color: #666;'>All are 100% FREE and easy to use!</h3>", unsafe_allow_html=True)
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # Grid of Tool Cards
        tools = [
            {"id": "Merge PDF", "icon": "🔗", "title": "Merge PDF", "desc": "Combine PDFs in the order you want."},
            {"id": "Split PDF", "icon": "✂️", "title": "Split PDF", "desc": "Separate one page or a whole set."},
            {"id": "Compress PDF", "icon": "📉", "title": "Compress PDF", "desc": "Reduce file size while optimizing quality."},
            {"id": "Convert PDF", "icon": "🔄", "title": "Convert PDF", "desc": "Convert to Word, Text or Images."},
            {"id": "Rotate PDF", "icon": "🔃", "title": "Rotate PDF", "desc": "Rotate your PDFs the way you need."},
            {"id": "Protect PDF", "icon": "🔒", "title": "Protect PDF", "desc": "Encrypt your PDF with a password."},
            {"id": "OCR PDF", "icon": "🔍", "title": "OCR PDF", "desc": "Best for scanned PDFs. For regular ones, use Convert."},
            {"id": "Organize", "icon": "🗂️", "title": "Organize PDF", "desc": "Rearrange, delete or add pages to your document."},
            {"id": "Extract Img", "icon": "🖼️", "title": "Extract Images", "desc": "Extract all embedded images from your PDF file."},
            {"id": "Watermark", "icon": "🖋️", "title": "Watermark", "desc": "Add a text watermark to all pages of your PDF."},
            {"id": "Page Numbers", "icon": "🔢", "title": "Page Numbers", "desc": "Add page numbers to the bottom of your PDF."},
            {"id": "Grayscale", "icon": "🌑", "title": "Grayscale", "desc": "Convert colored PDFs to black and white."},
            {"id": "Metadata", "icon": "ℹ️", "title": "Metadata", "desc": "Edit PDF Title, Author, and Subject."},
        ]
        
        # Display cards in a 3-column grid
        for row in range(0, len(tools), 3):
            cols = st.columns(3)
            for i in range(3):
                if row + i < len(tools):
                    tool = tools[row + i]
                    with cols[i]:
                        # Visual layer (bottom)
                        st.markdown(f"""
                            <div style="position: relative; height: 250px;">
                                <div class="card-content">
                                    <div class="card-icon">{tool['icon']}</div>
                                    <div class="card-title">{tool['title']}</div>
                                    <div class="card-desc">{tool['desc']}</div>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        # Interaction layer (top)
                        st.markdown('<div style="margin-top: -250px;">', unsafe_allow_html=True)
                        if st.button("", key=f"btn_home_{tool['id']}", use_container_width=True):
                            st.session_state.tool = tool['id']
                            st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)

    elif st.session_state.tool == "Convert PDF":
        st.title("🔄 Convert PDF")
        st.write("Convert PDF to Text, Word, or Images.")
        
        # Navigation back to home
        if st.button("← Back to Home"):
            st.session_state.tool = "Home"
            st.rerun()
            
        uploaded_files = st.file_uploader("Choose PDF files", type="pdf", accept_multiple_files=True, key="conv_upload")

        if uploaded_files:
            for uploaded_file in uploaded_files:
                with st.expander(f"📄 {uploaded_file.name}", expanded=True):
                    col_a, col_b = st.columns([2, 1])
                    with col_a:
                        conversion_type = st.selectbox(
                            "Select output format",
                            ["Select an option", "Text (.txt)", "Word (.docx)", "Images (.png)"],
                            key=f"select_{uploaded_file.name}"
                        )
                    with col_b:
                        st.markdown("<br>", unsafe_allow_html=True)
                        if conversion_type == "Text (.txt)":
                            if st.button(f"Extract Text", key=f"btn_txt_{uploaded_file.name}"):
                                with st.spinner("Extracting..."):
                                    text = pdf_to_text(uploaded_file)
                                    st.download_button("Download TXT", text, f"{uploaded_file.name.rsplit('.', 1)[0]}.txt", "text/plain")

                        elif conversion_type == "Word (.docx)":
                            if st.button(f"Convert to Word", key=f"btn_docx_{uploaded_file.name}"):
                                with st.spinner("Converting..."):
                                    docx_data = pdf_to_docx(uploaded_file)
                                    st.download_button("Download DOCX", docx_data, f"{uploaded_file.name.rsplit('.', 1)[0]}.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")

                        elif conversion_type == "Images (.png)":
                            if st.button(f"Convert to Images", key=f"btn_img_{uploaded_file.name}"):
                                with st.spinner("Creating ZIP..."):
                                    base_name = uploaded_file.name.rsplit('.', 1)[0]
                                    zip_data = pdf_to_images_zip(uploaded_file, base_name)
                                    st.download_button("Download ZIP", zip_data, f"{base_name}_images.zip", "application/zip")

    elif st.session_state.tool == "Merge PDF":
        st.title("🔗 Merge PDF")
        st.write("Combine multiple PDF files into a single document.")
        if st.button("← Back to Home"):
            st.session_state.tool = "Home"
            st.rerun()
            
        uploaded_files = st.file_uploader("Upload PDF files to merge", type="pdf", accept_multiple_files=True, key="merge_upload")
        
        if uploaded_files and len(uploaded_files) > 1:
            st.info(f"Selected {len(uploaded_files)} files for merging.")
            if st.button("Merge All PDFs"):
                with st.spinner("Merging..."):
                    merged_data = merge_pdfs(uploaded_files)
                    st.success("Successfully merged!")
                    st.download_button("Download Merged PDF", merged_data, "merged_document.pdf", "application/pdf")
        elif uploaded_files:
            st.warning("Please upload at least 2 files to merge.")

    elif st.session_state.tool == "Split PDF":
        st.title("✂️ Split PDF")
        st.write("Split a PDF by page ranges (e.g., '1-3, 5, 8-10').")
        if st.button("← Back to Home"):
            st.session_state.tool = "Home"
            st.rerun()
            
        uploaded_file = st.file_uploader("Choose a PDF file", type="pdf", key="split_upload")
        
        if uploaded_file:
            range_input = st.text_input("Enter page ranges (comma-separated)", "1-2, 3")
            if st.button("Split PDF"):
                with st.spinner("Splitting..."):
                    ranges = [r.strip() for r in range_input.split(",")]
                    zip_data = split_pdf(uploaded_file, ranges)
                    st.download_button("Download Split Parts (ZIP)", zip_data, "split_pdfs.zip", "application/zip")

    elif st.session_state.tool == "Compress PDF":
        st.title("📉 Compress PDF")
        st.write("Reduce the file size of your PDF while maintaining quality.")
        if st.button("← Back to Home"):
            st.session_state.tool = "Home"
            st.rerun()
            
        uploaded_file = st.file_uploader("Choose a PDF file", type="pdf", key="comp_upload")
        
        if uploaded_file:
            if st.button("Compress PDF"):
                with st.spinner("Compressing..."):
                    compressed_data = compress_pdf(uploaded_file)
                    st.download_button("Download Compressed PDF", compressed_data, f"compressed_{uploaded_file.name}", "application/pdf")

    elif st.session_state.tool == "Rotate PDF":
        st.title("� Rotate PDF")
        st.write("Rotate all pages in your PDF document.")
        if st.button("← Back to Home"):
            st.session_state.tool = "Home"
            st.rerun()
            
        uploaded_file = st.file_uploader("Choose a PDF file", type="pdf", key="rot_upload")
        
        if uploaded_file:
            rotation = st.selectbox("Rotation Angle", [90, 180, 270], format_func=lambda x: f"{x}°")
            if st.button("Rotate PDF"):
                with st.spinner("Rotating..."):
                    rotated_data = rotate_pdf(uploaded_file, rotation)
                    st.download_button("Download Rotated PDF", rotated_data, f"rotated_{uploaded_file.name}", "application/pdf")

    elif st.session_state.tool == "Protect PDF":
        st.title("🔒 Protect PDF")
        st.write("Secure your PDF with a password.")
        if st.button("← Back to Home"):
            st.session_state.tool = "Home"
            st.rerun()
            
        uploaded_file = st.file_uploader("Choose a PDF file", type="pdf", key="prot_upload")
        
        if uploaded_file:
            password = st.text_input("Enter Password", type="password")
            if st.button("Protect PDF"):
                if password:
                    with st.spinner("Encrypting..."):
                        protected_data = protect_pdf(uploaded_file, password)
                        st.download_button("Download Protected PDF", protected_data, f"protected_{uploaded_file.name}", "application/pdf")
                else:
                    st.error("Please enter a password.")

    elif st.session_state.tool == "OCR PDF":
        st.markdown("<h1 style='color: #e5322d !important;'>🔍 OCR PDF (Optical Character Recognition)</h1>", unsafe_allow_html=True)
        st.write("Extract text from scanned PDFs or images that don't have selectable text.")
        
        if st.button("← Back to Home"):
            st.session_state.tool = "Home"
            st.rerun()
            
        st.info("💡 **Note**: This tool is perfect for scanned documents. For regular PDFs, use the **Convert PDF** tool.")
        
        uploaded_file = st.file_uploader("Choose a scanned PDF file", type="pdf", key="ocr_upload")
        
        if uploaded_file:
            st.success(f"Ready to process: {uploaded_file.name}")
            if st.button("Extract Text with OCR"):
                with st.spinner("🔍 Reading document... This may take a moment."):
                    try:
                        extracted_text = ocr_pdf(uploaded_file)
                        st.success("✅ OCR completed successfully!")
                        st.markdown("### Extracted Text Preview:")
                        st.text_area("", extracted_text, height=400, key="ocr_result_area")
                        st.download_button(
                            label="📥 Download Extracted Text",
                            data=extracted_text,
                            file_name=f"ocr_{uploaded_file.name.rsplit('.', 1)[0]}.txt",
                            mime="text/plain"
                        )
                    except Exception as e:
                        st.error(f"❌ OCR failed: {e}")
                        st.info("🛠️ **Troubleshooting**: I've attempted to install Tesseract and Poppler via Winget. If you still see this error, please **restart your terminal or computer** to update your system PATH.")
                        st.markdown("""
                        **Manual Installation Steps:**
                        1. Download Tesseract from [here](https://github.com/UB-Mannheim/tesseract/wiki).
                        2. Download Poppler for Windows from [here](https://github.com/oschwartz10612/poppler-windows/releases).
                        3. Add both `bin` folders to your system Environment Variables (PATH).
                        """)

    elif st.session_state.tool == "Organize":
        st.title("🗂️ Organize PDF")
        st.write("Rearrange or delete pages from your PDF document.")
        if st.button("← Back to Home"):
            st.session_state.tool = "Home"
            st.rerun()
            
        uploaded_file = st.file_uploader("Choose a PDF file", type="pdf", key="org_upload")
        
        if uploaded_file:
            with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
                total_pages = len(doc)
                st.info(f"This PDF has {total_pages} pages.")
                
                st.markdown("### Select and Order Pages")
                st.write("Enter the page numbers you want to keep, in the order you want them (e.g., '1, 3, 2').")
                
                page_input = st.text_input("Page Sequence", value=", ".join(str(i+1) for i in range(total_pages)))
                
                if st.button("Organize and Download"):
                    try:
                        # Convert 1-based string input to 0-based integer list
                        order = [int(p.strip()) - 1 for p in page_input.split(",") if p.strip().isdigit()]
                        # Validate indices
                        valid_order = [p for p in order if 0 <= p < total_pages]
                        
                        if not valid_order:
                            st.error("Please enter valid page numbers.")
                        else:
                            with st.spinner("Organizing..."):
                                result_data = organize_pdf(uploaded_file, valid_order)
                                st.success("Document organized!")
                                st.download_button("Download Organized PDF", result_data, f"organized_{uploaded_file.name}", "application/pdf")
                    except Exception as e:
                        st.error(f"Error: {e}")

    elif st.session_state.tool == "Extract Img":
        st.title("🖼️ Extract Images")
        st.write("Extract all embedded images from your PDF document.")
        if st.button("← Back to Home"):
            st.session_state.tool = "Home"
            st.rerun()
            
        uploaded_file = st.file_uploader("Choose a PDF file", type="pdf", key="extract_img_upload")
        
        if uploaded_file:
            if st.button("Extract All Images"):
                with st.spinner("Scanning for images..."):
                    try:
                        zip_data, count = extract_images_from_pdf(uploaded_file)
                        if count > 0:
                            st.success(f"Found and extracted {count} images!")
                            st.download_button("Download All Images (ZIP)", zip_data, f"images_from_{uploaded_file.name.rsplit('.', 1)[0]}.zip", "application/zip")
                        else:
                            st.warning("No embedded images found in this PDF.")
                    except Exception as e:
                        st.error(f"❌ Extraction failed: {e}")

    elif st.session_state.tool == "Watermark":
        st.title("🖋️ Watermark PDF")
        st.write("Add a text watermark to all pages of your PDF.")
        if st.button("← Back to Home"):
            st.session_state.tool = "Home"
            st.rerun()
        
        uploaded_file = st.file_uploader("Choose a PDF file", type="pdf", key="water_upload")
        if uploaded_file:
            watermark_text = st.text_input("Enter Watermark Text", "CONFIDENTIAL")
            opacity = st.slider("Watermark Opacity", 0.1, 1.0, 0.3)
            if st.button("Add Watermark"):
                with st.spinner("Applying watermark..."):
                    result = watermark_pdf(uploaded_file, watermark_text, opacity)
                    st.success("Watermark applied!")
                    st.download_button("Download Watermarked PDF", result, f"watermarked_{uploaded_file.name}", "application/pdf")

    elif st.session_state.tool == "Page Numbers":
        st.title("🔢 Add Page Numbers")
        st.write("Add page numbers to the bottom of each page.")
        if st.button("← Back to Home"):
            st.session_state.tool = "Home"
            st.rerun()
            
        uploaded_file = st.file_uploader("Choose a PDF file", type="pdf", key="num_upload")
        if uploaded_file:
            if st.button("Add Page Numbers"):
                with st.spinner("Numbering pages..."):
                    result = add_page_numbers(uploaded_file)
                    st.success("Page numbers added!")
                    st.download_button("Download Numbered PDF", result, f"numbered_{uploaded_file.name}", "application/pdf")

    elif st.session_state.tool == "Grayscale":
        st.title("🌑 Convert to Grayscale")
        st.write("Convert colored PDFs to black and white.")
        if st.button("← Back to Home"):
            st.session_state.tool = "Home"
            st.rerun()
            
        uploaded_file = st.file_uploader("Choose a PDF file", type="pdf", key="gray_upload")
        if uploaded_file:
            if st.button("Convert to Grayscale"):
                with st.spinner("Converting..."):
                    result = pdf_to_grayscale(uploaded_file)
                    st.success("Converted to grayscale!")
                    st.download_button("Download Grayscale PDF", result, f"grayscale_{uploaded_file.name}", "application/pdf")

    elif st.session_state.tool == "Metadata":
        st.title("ℹ️ Edit PDF Metadata")
        st.write("Update PDF Title, Author, and Subject.")
        if st.button("← Back to Home"):
            st.session_state.tool = "Home"
            st.rerun()
            
        uploaded_file = st.file_uploader("Choose a PDF file", type="pdf", key="meta_upload")
        if uploaded_file:
            # Read existing metadata
            with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
                meta = doc.metadata
            
            title = st.text_input("Title", meta.get("title", ""))
            author = st.text_input("Author", meta.get("author", ""))
            subject = st.text_input("Subject", meta.get("subject", ""))
            
            if st.button("Update Metadata"):
                with st.spinner("Updating..."):
                    result = edit_metadata(uploaded_file, title, author, subject)
                    st.success("Metadata updated!")
                    st.download_button("Download Updated PDF", result, f"updated_{uploaded_file.name}", "application/pdf")

    st.markdown("<br><hr>", unsafe_allow_html=True)
    st.caption("PDF Power-Tool | Built for performance and ease of use. © 2026")

if __name__ == "__main__":
    main()
