import streamlit as st
import fitz  # PyMuPDF
from pdf2docx import Converter
import io
import os
import zipfile
from PIL import Image
from docx import Document

st.set_page_config(page_title="PDF Multi-Converter", page_icon="📄", layout="centered")

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

def main():
    st.title("📄 PDF Power-Tool")
    
    with st.sidebar:
        st.header("🛠️ Tools Menu")
        choice = st.radio(
            "Select a Tool",
            ["Convert PDF", "Merge PDF", "Split PDF", "Compress PDF", "Rotate PDF", "Protect PDF"]
        )
        
        st.divider()
        st.header("💡 How to use:")
        st.markdown(f"1. **Upload** your PDF(s).\n2. **Configure** {choice.lower()} options.\n3. **Download** result.")
        st.info("Powered by PyMuPDF, pdf2docx & Streamlit")

    if choice == "Convert PDF":
        st.header("🔄 Convert PDF")
        st.write("Convert PDF to Text, Word, or Images.")
        uploaded_files = st.file_uploader("Choose PDF files", type="pdf", accept_multiple_files=True, key="conv_upload")

        if uploaded_files:
            for uploaded_file in uploaded_files:
                with st.expander(f"📄 {uploaded_file.name}"):
                    conversion_type = st.selectbox(
                        "Output Format",
                        ["Select an option", "Text (.txt)", "Word (.docx)", "Images (.png)"],
                        key=f"select_{uploaded_file.name}"
                    )

                    if conversion_type == "Text (.txt)":
                        if st.button(f"Extract Text", key=f"btn_txt_{uploaded_file.name}"):
                            with st.spinner("Extracting..."):
                                text = pdf_to_text(uploaded_file)
                                st.text_area("Preview", text, height=200, key=f"text_{uploaded_file.name}")
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

    elif choice == "Merge PDF":
        st.header("🔗 Merge PDF")
        st.write("Combine multiple PDF files into a single document.")
        uploaded_files = st.file_uploader("Upload PDF files to merge", type="pdf", accept_multiple_files=True, key="merge_upload")
        
        if uploaded_files and len(uploaded_files) > 1:
            if st.button("Merge All PDFs"):
                with st.spinner("Merging..."):
                    merged_data = merge_pdfs(uploaded_files)
                    st.success("Successfully merged!")
                    st.download_button("Download Merged PDF", merged_data, "merged_document.pdf", "application/pdf")
        elif uploaded_files:
            st.warning("Please upload at least 2 files to merge.")

    elif choice == "Split PDF":
        st.header("✂️ Split PDF")
        st.write("Split a PDF by page ranges (e.g., '1-3, 5, 8-10').")
        uploaded_file = st.file_uploader("Choose a PDF file", type="pdf", key="split_upload")
        
        if uploaded_file:
            range_input = st.text_input("Enter page ranges (comma-separated)", "1-2, 3")
            if st.button("Split PDF"):
                with st.spinner("Splitting..."):
                    ranges = [r.strip() for r in range_input.split(",")]
                    zip_data = split_pdf(uploaded_file, ranges)
                    st.download_button("Download Split Parts (ZIP)", zip_data, "split_pdfs.zip", "application/zip")

    elif choice == "Compress PDF":
        st.header("📉 Compress PDF")
        st.write("Reduce the file size of your PDF.")
        uploaded_file = st.file_uploader("Choose a PDF file", type="pdf", key="comp_upload")
        
        if uploaded_file:
            if st.button("Compress PDF"):
                with st.spinner("Compressing..."):
                    compressed_data = compress_pdf(uploaded_file)
                    st.download_button("Download Compressed PDF", compressed_data, f"compressed_{uploaded_file.name}", "application/pdf")

    elif choice == "Rotate PDF":
        st.header("🔄 Rotate PDF")
        st.write("Rotate all pages in your PDF.")
        uploaded_file = st.file_uploader("Choose a PDF file", type="pdf", key="rot_upload")
        
        if uploaded_file:
            rotation = st.selectbox("Rotation Angle", [90, 180, 270], format_func=lambda x: f"{x}°")
            if st.button("Rotate PDF"):
                with st.spinner("Rotating..."):
                    rotated_data = rotate_pdf(uploaded_file, rotation)
                    st.download_button("Download Rotated PDF", rotated_data, f"rotated_{uploaded_file.name}", "application/pdf")

    elif choice == "Protect PDF":
        st.header("🔒 Protect PDF")
        st.write("Add a password to your PDF document.")
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

    st.divider()
    st.caption("Custom PDF Toolset - Open Source Alternative to iLovePDF")

if __name__ == "__main__":
    main()
