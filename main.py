from utils import resume_parser as rp


def main():
    pdf_path = 'docs/resume_1.pdf'
    parser = rp.ResumeParser()
    resume_text = parser.extract_text_from_pdf(pdf_path=pdf_path)
    print(resume_text)



if __name__ == "__main__":
    main()
