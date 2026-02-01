# PDF Power-Tool

A powerful, open-source alternative to iLovePDF built with Streamlit and PyMuPDF.

## Features
- **🔄 Convert PDF**: Convert to Text (.txt), Word (.docx), or Images (.png - bundled in ZIP).
- **🔗 Merge PDF**: Combine multiple PDF files into one.
- **✂️ Split PDF**: Split documents by specific page ranges.
- **📉 Compress PDF**: Reduce PDF file size.
- **� Rotate PDF**: Rotate all pages in a document.
- **🔒 Protect PDF**: Add AES-256 password protection to your files.
- **🔍 OCR PDF**: Extract text from scanned documents using Optical Character Recognition.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/bazougaa/PDF-converter.git
   cd PDF-converter
   ```

2. Install dependencies:
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
