# PDF Power-Tool

A powerful, open-source alternative to iLovePDF built with Streamlit and PyMuPDF.

## Features
- **🔄 Convert PDF**: Convert to Text (.txt), Word (.docx), or Images (.png - bundled in ZIP).
- **🔗 Merge PDF**: Combine multiple PDF files into one.
- **✂️ Split PDF**: Split documents by specific page ranges.
- **📉 Compress PDF**: Reduce PDF file size.
- **🔃 Rotate PDF**: Rotate all pages in a document.
- **🔒 Protect PDF**: Add AES-256 password protection to your files.
- **🔍 OCR PDF**: Extract text from scanned documents using Optical Character Recognition. (Note: Best for scanned documents; for regular PDFs, use **Convert PDF**). Supports **English** and **Arabic**.
- **🗂️ Organize PDF**: Rearrange or delete pages in a document.
- **🖼️ Extract Images**: Extract all embedded images from a PDF file.
- **🖋️ Watermark PDF**: Add a text watermark to every page.
- **🔢 Page Numbers**: Automatically number all pages in a custom format.
- **🌑 PDF to Grayscale**: Convert colored PDFs to black and white to save ink.
- **ℹ️ Metadata Editor**: Change the PDF's Title, Author, and Subject.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/bazougaa/PDF-converter.git
   cd PDF-converter
   ```

2. **System Requirements (OCR Only)**:
   The OCR tool requires **Tesseract-OCR** to be installed on your system:
   - **Windows**: Download the installer from [UB-Mannheim Tesseract](https://github.com/UB-Mannheim/tesseract/wiki). Add the installation path (usually `C:\Program Files\Tesseract-OCR`) to your system **PATH**.
   - **Linux**: `sudo apt install tesseract-ocr`
   - **macOS**: `brew install tesseract`

3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
Run the application using Streamlit:
```bash
streamlit run app.py
```

## Technologies
- [Streamlit](https://streamlit.io/)
- [PyMuPDF](https://pymupdf.readthedocs.io/)
- [pdf2docx](https://dothinking.github.io/pdf2docx/)
