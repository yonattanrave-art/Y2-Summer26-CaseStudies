import os
import tkinter as tk
from tkinter import filedialog
from pypdf import PdfReader
from anthropic import Anthropic
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()
client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(url, key)

chat_history = []

def get_pdf_text():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Select your CV / Resume",
        filetypes=[("PDF files", "*.pdf")]
    )
    if not file_path:
        return "", "", ""
    
    file_name = os.path.basename(file_path)
    print(f"\nPDF '{file_name}' attached! \nType your message and press Enter to send. \nType /remove to unattach.")
    
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text, file_name, file_path

tools = [
    {
        "name": "save_candidate_profile",
        "description": "Save the finalized candidate profile, extracted details, and upload their resume file to the Co-Impact database when the review is complete.",
        "input_schema": {
            "type": "object",
            "properties": {
                "full_name": {"type": "string", "description": "Candidate full name"},
                "phone": {"type": "string", "description": "Candidate phone number"},
                "email": {"type": "string", "description": "Candidate email address"},
                "location": {"type": "string", "description": "Candidate city or location"},
                "skills": {"type": "string", "description": "Technical and soft skills"},
                "languages": {"type": "string", "description": "Languages and proficiency levels (Hebrew, Arabic, English)"},
                "education": {"type": "string", "description": "Degrees, institutions, and graduation dates"},
                "experience": {"type": "string", "description": "Key job titles, companies, and responsibilities"}
            },
            "required": ["full_name", "phone", "email", "location", "skills", "languages", "education", "experience"]
        }
    }
]

def agent1(chat_history):
    
    system_message = "You are the AI Assistant for *Co-Impact*, an organization dedicated to integrating Arab job seekers into high-quality employment. Your objective is to review incoming candidate resumes, ensure that critical information is complete, be brief, and minimized, assist in fixing gaps, but make sure that the user isn't lost. upload finalized resumes to the Co-Impact database. After the user uploads his resume . start with a greeting and then give your response. Analyze the candidate's resume for essential components:   - **Contact Details:** Full Name, Phone, Email, Location.    - **Work Experience:** Job titles, company names, dates, key responsibilities, and achievements.   - **Education:** Degrees/diplomas, institutions. - **Skills & Languages:** Technical/soft skills. before aploading the resumes, ask for the user permission to do so."
 
    is_first_message = True
    current_pdf_text = ""
    current_pdf_name = ""
    current_pdf_path = ""

    while True:
        if is_first_message:
            print("\nWould you like to upload a CV/Resume PDF? (Optional)")
            current_pdf_text, current_pdf_name, current_pdf_path = get_pdf_text()
            is_first_message = False

        user_input = input('\nYou: ')

        if user_input.lower() == 'exit':
            print("\nExiting the chat...")
            print("Thank you for using ResuFlow. Goodbye!")
            break

        if user_input.lower() == '/file':
            print("Opening file explorer...")
            current_pdf_text, current_pdf_name, current_pdf_path = get_pdf_text()
            continue

        if user_input.lower() == '/remove':
            current_pdf_text = ""
            current_pdf_name = ""
            current_pdf_path = ""
            print("\n[PDF unattached.]")
            continue

        if not user_input and not current_pdf_text:
            print("Please enter a message or select a file.")
            continue

        if current_pdf_text:
            if user_input:
                message_content = f"Here is my resume content (File: {current_pdf_name}):\n{current_pdf_text}\n\nAdditional message: {user_input}"
            else:
                message_content = f"Here is my resume content (File: {current_pdf_name}):\n{current_pdf_text}"
        else:
            message_content = user_input

        chat_history.append({'role': 'user', 'content': message_content})
        
        try:
            response = client.messages.create(
                model='claude-haiku-4-5-20251001',
                max_tokens=750,
                temperature=0.6,
                system=system_message,
                tools=tools,
                messages=chat_history
            )
            
            if response.stop_reason == "tool_use":
                tool_use_block = next(block for block in response.content if block.type == "tool_use")
                tool_input = tool_use_block.input
                
                print("\n[CO-IMPACT LIBRARY SYSTEM: Uploading to Supabase Database & Storage...]")
                
                resume_url = ""
                if current_pdf_path and os.path.exists(current_pdf_path):
                    with open(current_pdf_path, 'rb') as f:
                        file_data = f.read()
                    storage_path = f"resumes/{current_pdf_name}"
                    supabase.storage.from_("candidate_files").upload(
                        path=storage_path,
                        file=file_data,
                        file_options={"content-type": "application/pdf"}
                    )
                    resume_url = supabase.storage.from_("candidate_files").get_public_url(storage_path)

                supabase.table("candidates").insert({
                    "full_name": tool_input.get('full_name'),
                    "phone": tool_input.get('phone'),
                    "email": tool_input.get('email'),
                    "location": tool_input.get('location'),
                    "skills": tool_input.get('skills'),
                    "languages": tool_input.get('languages'),
                    "education": tool_input.get('education'),
                    "experience": tool_input.get('experience'),
                    "resume_url": resume_url
                }).execute()

                print("[Candidate successfully stored in Supabase database and storage!]\n")
                
                chat_history.append({'role': 'assistant', 'content': response.content})
                chat_history.append({
                    'role': 'user',
                    'content': [
                        {
                            'type': 'tool_result',
                            'tool_use_id': tool_use_block.id,
                            'content': 'Candidate profile and resume successfully saved to the Co-Impact Supabase database.'
                        }
                    ]
                })
                
                follow_up_response = client.messages.create(
                    model='claude-haiku-4-5-20251001',
                    max_tokens=750,
                    temperature=0.6,
                    system=system_message,
                    tools=tools,
                    messages=chat_history
                )
                reply = follow_up_response.content[0].text
                print(f'ResuFlow: {reply}')
                chat_history.append({'role': 'assistant', 'content': f"ResuFlow: {reply}"})
            else:
                reply = response.content[0].text
                print(f'ResuFlow: {reply}')
                chat_history.append({'role': 'assistant', 'content': f"ResuFlow: {reply}"})

            current_pdf_text = ""
            current_pdf_name = ""
            current_pdf_path = ""

        except Exception as e:
            print(f"Something went wrong: {e}")

agent1(chat_history)