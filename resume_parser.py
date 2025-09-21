import os
from io import BytesIO
from PyPDF2 import PdfReader
import docx

# For simplicity, we define a static list of skills.
SKILL_KEYWORDS = ["Python", "Java", "C++", "SQL", "AWS", "TensorFlow", "React", "Node.js", "docker", "kubernetes", "cloud", "agile", "scrum"]

def extract_text(file_obj, filename):
    """
    Extracts text from a file-like object based on its filename extension.
    
    Args:
        file_obj (BytesIO): The file-like object containing the file data.
        filename (str): The original name of the file, used to determine its type.
    
    Returns:
        str: The extracted text or an error message.
    """
    ext = os.path.splitext(filename)[1]
    text = ""
    try:
        if ext == ".pdf":
            # PyPDF2 can read directly from a file-like object
            reader = PdfReader(file_obj)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

        elif ext == ".docx":
            # docx library can read directly from a file-like object
            doc = docx.Document(file_obj)
            text = "\n".join([p.text for p in doc.paragraphs])

        elif ext == ".txt":
            # For plain text files, decode the bytes
            text = file_obj.read().decode("utf-8", errors="ignore")

        else:
            return f"[Extraction failed: Unsupported file type: {ext}]"

    except Exception as e:
        return f"[Extraction failed: {e}]"

    # Clean up and return the extracted text
    return str(text.strip())