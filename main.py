# importing libraries
import streamlit as st
import pandas as pd
import base64, random
import time, datetime
#libraries to parse the resume pdf files
# from pyresparser import ResumeParser  # Commented out due to issues
import PyPDF2
import re
from pdfminer3.layout import LAParams, LTTextBox
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager
from pdfminer3.pdfinterp import PDFPageInterpreter
from pdfminer3.converter import TextConverter
import io, random
from streamlit_tags import st_tags
from PIL import Image
import sqlite3  # Updated for SQLite
import nltk
nltk.download('stopwords')

# Check if spaCy model is available
try:
    import spacy
    nlp = spacy.load('en_core_web_sm')
    SPACY_AVAILABLE = True
except (ImportError, OSError) as e:
    SPACY_AVAILABLE = False
    st.error("spaCy English model not found. Install it using: python -m spacy download en_core_web_sm")

connection = sqlite3.connect('resume_analyzer.db', check_same_thread=False)
cursor = connection.cursor()

def create_table():
    """Create the user_data table if it doesn't exist"""
    db_table_name = 'user_data'
    table_sql = f"""
        CREATE TABLE IF NOT EXISTS {db_table_name} (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT NOT NULL,
            Email_ID TEXT NOT NULL,
            resume_score TEXT NOT NULL,
            Timestamp TEXT NOT NULL,
            Page_no TEXT NOT NULL,
            Predicted_Field TEXT NOT NULL,
            User_level TEXT NOT NULL,
            Actual_skills TEXT NOT NULL,
            Recommended_skills TEXT NOT NULL,
            Recommended_courses TEXT NOT NULL
        );
    """
    cursor.execute(table_sql)
    connection.commit()

def insert_data(name, email, res_score, timestamp, no_of_pages, reco_field, cand_level, skills, recommended_skills, courses):
    insert_record = f"""
        INSERT INTO user_data (
            Name, Email_ID, resume_score, Timestamp, Page_no,
            Predicted_Field, User_level, Actual_skills,
            Recommended_skills, Recommended_courses
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """
    rec_values = (name, email, res_score, timestamp, no_of_pages,
                  reco_field, cand_level, skills,
                  recommended_skills, courses)
    cursor.execute(insert_record, rec_values)
    connection.commit()

def get_table_download_link(df, filename, text):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href

# Alternative resume parser function
def extract_resume_data(pdf_path):
    """
    Alternative resume parsing function using PyPDF2 and regex
    """
    try:
        # Extract text from PDF
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
        
        # Basic data extraction using regex
        resume_data = {
            'name': extract_name(text),
            'email': extract_email(text),
            'mobile_number': extract_phone(text),
            'skills': extract_skills(text),
            'no_of_pages': len(pdf_reader.pages),
            'total_experience': extract_experience(text)
        }
        
        return resume_data
    except Exception as e:
        st.error(f"Error extracting resume data: {str(e)}")
        return None

def extract_name(text):
    """Extract name from resume text"""
    # Look for name patterns (first line or after "Name:")
    lines = text.split('\n')
    for line in lines[:5]:  # Check first 5 lines
        line = line.strip()
        if len(line) > 2 and len(line.split()) <= 4:
            # Simple heuristic: if it's not email/phone and has 1-4 words
            if not re.search(r'[@.]', line) and not re.search(r'\d{10}', line):
                return line
    return "Unknown"

def extract_email(text):
    """Extract email from resume text"""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    return emails[0] if emails else "Not found"

def extract_phone(text):
    """Extract phone number from resume text"""
    phone_pattern = r'(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    phones = re.findall(phone_pattern, text)
    return ''.join(phones[0]) if phones else "Not found"

def extract_skills(text):
    """Extract skills from resume text"""
    # Common skills keywords
    all_skills = [
        'python', 'java', 'javascript', 'html', 'css', 'react', 'node.js', 'django',
        'flask', 'sql', 'mysql', 'postgresql', 'mongodb', 'git', 'docker', 'kubernetes',
        'aws', 'azure', 'machine learning', 'deep learning', 'tensorflow', 'keras',
        'pytorch', 'pandas', 'numpy', 'scikit-learn', 'matplotlib', 'seaborn',
        'tableau', 'power bi', 'excel', 'r', 'c++', 'c#', '.net', 'spring boot',
        'android', 'ios', 'swift', 'kotlin', 'flutter', 'react native',
        'photoshop', 'illustrator', 'figma', 'sketch', 'adobe xd'
    ]
    
    text_lower = text.lower()
    found_skills = []
    
    for skill in all_skills:
        if skill in text_lower:
            found_skills.append(skill.title())
    
    return found_skills[:10]  # Return max 10 skills

def extract_experience(text):
    """Extract years of experience from resume text"""
    # Look for experience patterns
    exp_patterns = [
        r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
        r'experience\s*:?\s*(\d+)\+?\s*years?',
        r'(\d+)\+?\s*years?\s*in\s*'
    ]
    
    for pattern in exp_patterns:
        matches = re.findall(pattern, text.lower())
        if matches:
            return int(matches[0])
    
    return 0  # Default to 0 if no experience found

def pdf_reader(file):
    """Extract text from PDF using pdfminer3"""
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams(detect_vertical=True))
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
    with open(file,'rb') as fh:
        for page in PDFPage.get_pages(fh, caching=True, check_extractable=True):
            page_interpreter.process_page(page)
        text = fake_file_handle.getvalue()
    converter.close()
    fake_file_handle.close()
    return text

def show_pdf(file_path):
    with open(file_path,'rb') as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

def run():
    img = Image.open('Logo/resume_img.png')
    img.resize((250,250))
    st.image(img)
    st.title('AI Resume Analyzer')
    st.sidebar.markdown('# Choose User')
    activites = ['User', 'Admin']
    choice = st.sidebar.selectbox('Choose among the options:', activites)
    
    # Initialize database table (SQLite doesn't need CREATE DATABASE)
    create_table()

    if choice=='User':
        st.markdown('''<h5 style='text-align: left; color: #FCF90E;'> Upload your resume, and get smart recommendations</h5>''', unsafe_allow_html=True)
        pdf_file = st.file_uploader('Upload your Resume', type=['pdf'])
        if pdf_file is not None:
            with st.spinner('Uploading your Resume . . .'):
                time.sleep(4)
            save_pdf_path = './Uploaded_Resumes/' + pdf_file.name
            
            # Create directory if it doesn't exist
            import os
            os.makedirs('./Uploaded_Resumes', exist_ok=True)
            
            with open(save_pdf_path, 'wb') as f:
                f.write(pdf_file.getbuffer())
            show_pdf(save_pdf_path)
            
            try:
                # Use alternative resume parser instead of pyresparser
                resume_data = extract_resume_data(save_pdf_path)
                if not resume_data:
                    st.error("Failed to extract resume data. Please check your PDF file.")
                    return
            except Exception as e:
                st.error(f"Error parsing resume: {str(e)}")
                st.info("This might be due to a corrupted PDF file or unsupported format.")
                return
            if resume_data['total_experience']:
                print('\n\n\n'+ str(resume_data['total_experience'])+'\n\n\n')
            else: 
                print('\n\n\nhi\n\n\n')
            if resume_data:
                #get all the resume data
                resume_text = pdf_reader(save_pdf_path)

                st.header('Resume Analysis')
                st.success('Hello ' + resume_data['name'])
                st.subheader('Your Basic Info')
                try:
                    st.text('NAME         : '+ resume_data['name'])
                    st.text('EMAIL        : '+ resume_data['email'])
                    st.text('CONTACT      : '+ resume_data['mobile_number'])
                    st.text('RESUME PAGES : '+ str(resume_data['no_of_pages']))
                except:
                    pass
                
                cand_level = ''
                if resume_data['total_experience'] < 3:
                    cand_level = "Fresher"
                    st.markdown( '''<h4 style='text-align: center; color: #d73b5c;'>You are at Fresher level!</h4>''',unsafe_allow_html=True)
                elif resume_data['total_experience'] >= 3 and resume_data['total_experience'] <=10:
                    cand_level = "Intermediate"
                    st.markdown('''<h4 style='text-align: center; color: #1ed760;'>You are at intermediate level!</h4>''',unsafe_allow_html=True)
                elif resume_data['no_of_pages'] > 10:
                    cand_level = "Experienced"
                    st.markdown('''<h4 style='text-align: center; color: #fba171;'>You are at experience level!</h4>''',unsafe_allow_html=True)

                st.subheader('Skills Recommendation')
                keywords = st_tags(label='#### Your Current Skills', text='See our recommended skills below', value=resume_data['skills'], key='1  ')

                ##  keywords
                ds_keyword = ['tensorflow','keras','pytorch','machine learning','deep Learning','flask','streamlit']
                web_keyword = ['react', 'django', 'node jS', 'react js', 'php', 'laravel', 'magento', 'wordpress',
                               'javascript', 'angular js', 'c#', 'flask']
                android_keyword = ['android','android development','flutter','kotlin','xml','kivy']
                ios_keyword = ['ios','ios development','swift','cocoa','cocoa touch','xcode']
                uiux_keyword = ['ux','adobe xd','figma','zeplin','balsamiq','ui','prototyping','wireframes','storyframes','adobe photoshop','photoshop','editing','adobe illustrator','illustrator','adobe after effects','after effects','adobe premier pro','premier pro','adobe indesign','indesign','wireframe','solid','grasp','user research','user experience']

                recommended_skills = []
                reco_field = ''

                # Only skills and field recommendation, no course/certificate or video recommendations
                for i in resume_data['skills']:
                    
                    #data science recommendation
                    if i.lower() in ds_keyword:
                        reco_field = 'Data Science'
                        st.success('Our Analysis says you are looking for a Data Science Job')
                        recommended_skills = ['Data Visualization','Predictive Analysis','Statistical Modeling','Data Mining','Clustering & Classification','Data Analytics','Quantitative Analysis','Web Scraping','ML Algorithms','Keras','Pytorch','Probability','Scikit-learn','Tensorflow',"Flask",'Streamlit']
                        recommended_keywords = st_tags(label='### Recommended skills for you.', text='Recommended skills generated from System', value=recommended_skills, key = '2')
                        st.markdown('''<h4 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost the chances of getting a Job</h4>''',unsafe_allow_html=True)
                        break
                    
                    ## Web development recommendation
                    elif i.lower() in web_keyword:
                        print(i.lower())
                        reco_field = 'Web Development'
                        st.success("Our analysis says you are looking for Web Development Jobs")
                        recommended_skills = ['React','Django','Node JS','React JS','php','laravel','Magento','wordpress','Javascript','Angular JS','c#','Flask','SDK']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                        text='Recommended skills generated from System',value=recommended_skills,key = '3')
                        st.markdown('''<h4 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost the chances of getting a Job</h4>''',unsafe_allow_html=True)
                        break

                    ## Android App Development
                    elif i.lower() in android_keyword:
                        print(i.lower())
                        reco_field = 'Android Development'
                        st.success("Our analysis says you are looking for Android App Development Jobs")
                        recommended_skills = ['Android','Android development','Flutter','Kotlin','XML','Java','Kivy','GIT','SDK','SQLite']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                        text='Recommended skills generated from System',value=recommended_skills,key = '4')
                        st.markdown('''<h4 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost the chances of getting a Job</h4>''',unsafe_allow_html=True)
                        break

                    ## IOS App Development
                    elif i.lower() in ios_keyword:
                        print(i.lower())
                        reco_field = 'IOS Development'
                        st.success("Our analysis says you are looking for IOS App Development Jobs")
                        recommended_skills = ['IOS','IOS Development','Swift','Cocoa','Cocoa Touch','Xcode','Objective-C','SQLite','Plist','StoreKit',"UI-Kit",'AV Foundation','Auto-Layout']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                        text='Recommended skills generated from System',value=recommended_skills,key = '5')
                        st.markdown('''<h4 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost the chances of getting a Job</h4>''',unsafe_allow_html=True)
                        break

                    ## Ui-UX Recommendation
                    elif i.lower() in uiux_keyword:
                        print(i.lower())
                        reco_field = 'UI-UX Development'
                        st.success("Our analysis says you are looking for UI-UX Development Jobs")
                        recommended_skills = ['UI','User Experience','Adobe XD','Figma','Zeplin','Balsamiq','Prototyping','Wireframes','Storyframes','Adobe Photoshop','Editing','Illustrator','After Effects','Premier Pro','Indesign','Wireframe','Solid','Grasp','User Research']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                        text='Recommended skills generated from System',value=recommended_skills,key = '6')
                        st.markdown('''<h4 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost the chances of getting a Job</h4>''',unsafe_allow_html=True)
                        break

                # insert into table
                ts = time.time()
                cur_date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                cur_time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                timestamp = str(cur_date+' '+cur_time)

                # Resume writing recommendations
                st.subheader('Resume Tips & Ideas')
                resume_score = 0
                if 'Objective' in resume_text:
                    resume_score = resume_score+20
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Objective</h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: #FE0523;'>[-] Please add your career objective, it will give your career intension to the Recruiters.</h4>''',unsafe_allow_html=True)

                if 'Declaration'  in resume_text:
                    resume_score = resume_score + 20
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Declaration</h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: #FE0523;'>[-] Please add Declaration. It will give the assurance that everything written on your resume is true and fully acknowledged by you</h4>''',unsafe_allow_html=True)

                if 'Hobbies' or 'Interests'in resume_text:
                    resume_score = resume_score + 20
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Hobbies</h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: #FE0523;'>[-] Please add Hobbies. It will show your personality to the Recruiters and give the assurance that you are fit for this role or not.</h4>''',unsafe_allow_html=True)

                if 'Achievements' or 'Skills' in resume_text:
                    resume_score = resume_score + 20
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Skills </h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: #FE0523;'>[-] Please add Skills. It will show that you are capable for the required position.</h4>''',unsafe_allow_html=True)

                if 'Projects' in resume_text:
                    resume_score = resume_score + 20
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Projects</h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: #FE0523;'>[-] Please add Projects. It will show that you have done work related the required position or not.</h4>''',unsafe_allow_html=True)

                st.subheader("Resume Score")
                st.markdown(
                    """
                    <style>
                        .stProgress > div > div > div > div {
                            background-color: #d73b5c;
                        }
                    </style>""",
                    unsafe_allow_html=True,
                )
                
                my_bar = st.progress(0)
                score = 0
                for percent_complete in range(resume_score):
                    score += 1
                    time.sleep(0.1)
                    my_bar.progress(percent_complete + 1)
                st.success('Your Resume Writing Score: ' +str(score))
                st.warning('Note: This score is based on your content that you have in Resume.')
                st.balloons()

                insert_data(resume_data['name'], resume_data['email'], str(resume_score), timestamp,
                              str(resume_data['no_of_pages']), reco_field, cand_level, str(resume_data['skills']),
                              str(recommended_skills), "")  # No course recommendations
                
                connection.commit()
            else:
                st.error('** Something went wrong **')

    
    else:
        ## Admin side
        st.success('Welcome to Admin Side')
        ad_user = st.text_input("Username")
        ad_password = st.text_input("Password", type='password')
        if st.button('Login'):
            if ad_user == 'admin' and ad_password == 'admin':
                st.success("Welcome Admin !")

                # Display Data
                cursor.execute('''SELECT * FROM user_data''')
                data = cursor.fetchall()
                st.header("User's Data")
                df = pd.DataFrame(data, columns=['ID', 'Name', 'Email', 'Resume Score', 'Timestamp', 'Total Page',
                                                 'Predicted Field', 'User Level', 'Actual Skills', 'Recommended Skills',
                                                 'Recommended Course'])
                st.dataframe(df)
                st.markdown(get_table_download_link(df,'User_Data.csv','Download Report'), unsafe_allow_html=True)
              

            else:
                st.error("Wrong ID & Password Provided")

if __name__ == "__main__":
    run()