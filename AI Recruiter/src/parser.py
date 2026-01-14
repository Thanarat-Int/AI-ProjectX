import pdfplumber
import docx
import os

def extract_text_from_pdf(file_path_or_buffer):
    """
    Extracts text from a PDF file.
    Args:
        file_path_or_buffer: Path to the PDF file or a file-like object.
    Returns:
        str: Extracted text.
    """
    text = ""
    try:
        with pdfplumber.open(file_path_or_buffer) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return None
    return text

def extract_text_from_docx(file_path_or_buffer):
    """
    Extracts text from a DOCX file.
    Args:
        file_path_or_buffer: Path to the DOCX file or a file-like object.
    Returns:
        str: Extracted text.
    """
    text = ""
    try:
        doc = docx.Document(file_path_or_buffer)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        print(f"Error reading DOCX: {e}")
        return None
    return text

def parse_resume(file):
    """
    Determines file type and extracts text accordingly.
    Args:
        file: Uploaded file object (Streamlit UploadedFile) or path.
    Returns:
        str: Extracted text.
    """
    if hasattr(file, 'name'):
        filename = file.name
    else:
        filename = str(file)

    if filename.lower().endswith('.pdf'):
        return extract_text_from_pdf(file)
    elif filename.lower().endswith('.docx'):
        return extract_text_from_docx(file)
    else:
        return "Unsupported file format."
