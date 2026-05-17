import re


def clean_text(text: str) -> str:
    # remove emails, phone numbers, URLs
    text = re.sub(r'\S+@\S+', '', text)
    text = re.sub(r'[\+\d][\d\s\-\(\)]{7,}', '', text)
    text = re.sub(r'http\S+', '', text)

    # remove extra whitespace and special characters
    text = re.sub(r'[^\w\s\.\,\-]', ' ', text)
    text = re.sub(r'\s+', ' ', text)

    return text.strip()