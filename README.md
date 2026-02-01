# PDF Multi-Converter

A Streamlit-based tool to convert PDF files to various formats including Text, Word (.docx), and Images (.png).

## Features
- **Multi-File Upload**: Process multiple PDFs at once.
- **Text Extraction**: Extract plain text using PyMuPDF.
- **Word Conversion**: Convert PDFs to editable .docx files using pdf2docx.
- **Image Conversion**: Export PDF pages as high-quality PNG images.

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
