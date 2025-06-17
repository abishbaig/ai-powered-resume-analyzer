# AI-Powered Resume Analyzer

This project is an AI-powered resume analyzer web application built with **Streamlit**. It allows users to upload their resumes in PDF format and receive smart, field-specific skill recommendations, resume writing tips, and a resume score. The application also provides an admin dashboard for managing and downloading user data.

## Features

- **Resume Upload:** Users can upload their resume in PDF format.
- **Resume Parsing:** Extracts key information such as name, email, phone, skills, and experience using NLP and regex.
- **Skill Recommendations:** Suggests relevant skills based on the user's current skills and field (e.g., Data Science, Web Development, Android, iOS, UI/UX).
- **Resume Tips:** Provides actionable tips to improve resume content.
- **Resume Scoring:** Gives a score based on the presence of important resume sections.
- **Admin Dashboard:** Allows admin to view and download all user data as a CSV file.

## How It Works

1. **User uploads a resume (PDF).**
2. The app extracts information and analyzes the content.
3. The user receives:
   - Their basic info (name, email, etc.)
   - Detected and recommended skills for their field
   - Resume writing tips and a resume score
4. **Admin** can log in to view/download all user data.

## Technologies Used

- [Streamlit](https://streamlit.io/) for the web interface
- [PyPDF2](https://pypi.org/project/PyPDF2/) and [pdfminer3](https://pypi.org/project/pdfminer3/) for PDF parsing
- [NLTK](https://www.nltk.org/) and [spaCy](https://spacy.io/) for NLP tasks
- [SQLite](https://www.sqlite.org/index.html) for data storage
- [Pandas](https://pandas.pydata.org/) for data handling

## Getting Started

### Prerequisites

- Python 3.8+
- pip

### Installation

1. **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/AI-Powered-Resume-Analyzer.git
    cd AI-Powered-Resume-Analyzer
    ```

2. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

    Example `requirements.txt`:
    ```
    streamlit
    pandas
    PyPDF2
    pdfminer3
    nltk
    spacy
    streamlit-tags
    pillow
    ```

3. **Download spaCy English model (optional, recommended):**
    ```bash
    python -m spacy download en_core_web_sm
    ```

### Running the App

```bash
streamlit run main.py
```

- Open the provided local URL in your browser.

## Usage

- **User:** Upload your resume and get instant feedback and recommendations.
- **Admin:** Log in with username `admin` and password `admin` to view/download all user data.

## Project Structure

```
AI-Powered Recruitment Agent/
│
├── main.py
├── requirements.txt
├── README.md
├── Logo/
│   └── resume_img.png
├── Uploaded_Resumes/
│   └── (uploaded files)
└── resume_analyzer.db
```

## Notes

- Only PDF resumes are supported.
- All user data is stored in a local SQLite database (`resume_analyzer.db`).
- No external course or video recommendations are included.

## License

This project is for educational purposes.

---