import pdfplumber
import spacy


# Load spaCy model
try:
    nlp = spacy.load('en_core_web_sm')
except:
    # If the model isn't downloaded, error
    print("SpaCy model not found. Please download using:")
    print("uv pip install pip\nuv run --with spacy spacy download en_core_web_sm")
    # Loading a simple model
    nlp = spacy.blank('en')


class ResumeParser:
    

    def extract_text_from_pdf(self, pdf_path):
        text = ''
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + '\n'
        return text.lower()