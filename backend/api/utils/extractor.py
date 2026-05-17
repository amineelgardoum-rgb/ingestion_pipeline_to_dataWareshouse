import pdfplumber


def extract_text(pdf_path: str) -> str:
    with pdfplumber.open(pdf_path) as pdf:
        pages = [
            page.extract_text()
            for page in pdf.pages
            if page.extract_text()
        ]
    if not pages:
        raise ValueError(f"Could not extract any text from: {pdf_path}")
    return "\n".join(pages)