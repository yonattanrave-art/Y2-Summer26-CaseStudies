import os
import tkinter as tk
from tkinter import filedialog
from pypdf import PdfReader
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
chat_history = []

def get_pdf_text():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Select your CV / Resume",
        filetypes=[("PDF files", "*.pdf")]
    )
    if not file_path:
        return ""
    
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def agent1(chat_history):
    
    system_message = "You are the AI Assistant for *Co-Impact*, an organization dedicated to integrating Arab job seekers into high-quality employment. Your objective is to review incoming candidate resumes, ensure all critical information is complete, assist in fixing gaps, and upload finalized resumes to the Co-Impact database.start with a greeting and then give your response. Analyze the candidate's resume for essential components:   - **Contact Details:** Full Name, Phone, Email, Location.    - **Work Experience:** Job titles, company names, dates, key responsibilities, and achievements.   - **Education:** Degrees/diplomas, institutions, graduation dates. - **Skills & Languages:** Technical/soft skills, proficiency levels (Hebrew, Arabic, English)."

    is_first_message = True

    while True:
        if is_first_message:
            print("Would you like to upload a CV/Resume PDF? (Optional)")
            pdf_text = get_pdf_text()
            user_input = input('\nYou: ')
            
            if pdf_text:
                user_input = f"Here is my resume content:\n{pdf_text}\n\nAdditional message: {user_input}"
            
            is_first_message = False
        else:
            user_input = input('\nYou: ')

        if user_input.lower() == 'exit':
            break

        chat_history.append({'role': 'user', 'content': user_input})
        
        try:
            response = client.messages.create(
                model='claude-haiku-4-5-20251001',
                max_tokens=2999,
                temperature=0.6,
                system=system_message,
                messages=chat_history
            )
            
            reply = response.content[0].text
            print(f'ResuFlow: {reply}')
            chat_history.append({'role': 'assistant', 'content': f"ResuFlow: {reply}"})

        except Exception as e:
            print(f"Something went wrong: {e}")

agent1(chat_history)