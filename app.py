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
    # pdf2docx requires physical files for conversion
    temp_pdf = "temp_input.pdf"
    temp_docx = "temp_output.docx"
    
    with open(temp_pdf, "wb") as f:
        f.write(pdf_file.getbuffer())
    
    cv = Converter(temp_pdf)
    cv.convert(temp_docx, start=0, end=None)
    cv.close()
    
    with open(temp_docx, "rb") as f:
        docx_data = f.read()
    
    # Cleanup
    os.remove(temp_pdf)
    os.remove(temp_docx)
    
    return docx_data

def main():
    st.title("📄 PDF Multi-Converter")
    
    with st.sidebar:
        st.header("How to use:")
        st.markdown("""
        1. **Upload** one or more PDF files.
        2. **Select** the desired output format for each file.
        3. **Click** the convert button.
        4. **Download** the resulting file.
        """)
        st.info("Supported formats: Text (.txt), Word (.docx), Images (.png)")

    st.write("Upload a PDF file and choose the format you want to convert it to.")

    uploaded_files = st.file_uploader("Choose PDF files", type="pdf", accept_multiple_files=True)

    if uploaded_files:
        for uploaded_file in uploaded_files:
            with st.expander(f"📄 {uploaded_file.name}"):
                st.info(f"File uploaded: {uploaded_file.name}")
                
                conversion_type = st.selectbox(
                    f"Select Conversion Format for {uploaded_file.name}",
                    ["Select an option", "Text (.txt)", "Word (.docx)", "Images (.png)"],
                    key=f"select_{uploaded_file.name}"
                )

                if conversion_type == "Text (.txt)":
                    if st.button(f"Convert {uploaded_file.name} to Text", key=f"btn_txt_{uploaded_file.name}"):
                        with st.spinner("Extracting text..."):
                            text = pdf_to_text(uploaded_file)
                            st.text_area("Extracted Text", text, height=300, key=f"text_{uploaded_file.name}")
                            st.download_button(
                                label="Download Text File",
                                data=text,
                                file_name=f"{uploaded_file.name.rsplit('.', 1)[0]}.txt",
                                mime="text/plain",
                                key=f"dl_txt_{uploaded_file.name}"
                            )

                elif conversion_type == "Word (.docx)":
                    if st.button(f"Convert {uploaded_file.name} to Word", key=f"btn_docx_{uploaded_file.name}"):
                        with st.spinner("Converting to Word... This might take a moment."):
                            try:
                                docx_data = pdf_to_docx(uploaded_file)
                                st.success("Conversion successful!")
                                st.download_button(
                                    label="Download Word Document",
                                    data=docx_data,
                                    file_name=f"{uploaded_file.name.rsplit('.', 1)[0]}.docx",
                                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                    key=f"dl_docx_{uploaded_file.name}"
                                )
                            except Exception as e:
                                st.error(f"An error occurred during conversion: {e}")

                elif conversion_type == "Images (.png)":
                    if st.button(f"Convert {uploaded_file.name} to Images", key=f"btn_img_{uploaded_file.name}"):
                        with st.spinner("Generating images and creating ZIP..."):
                            base_name = uploaded_file.name.rsplit('.', 1)[0]
                            zip_data = pdf_to_images_zip(uploaded_file, base_name)
                            st.success(f"Successfully converted {uploaded_file.name} to images!")
                            
                            st.download_button(
                                label="Download Images (ZIP)",
                                data=zip_data,
                                file_name=f"{base_name}_images.zip",
                                mime="application/zip",
                                key=f"dl_zip_{uploaded_file.name}"
                            )
    
    st.divider()
    st.caption("Powered by Streamlit, PyMuPDF, and pdf2docx")

if __name__ == "__main__":
    main()
