import os
from dotenv import load_dotenv
from supabase import create_client
import anthropic

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ANTHROPIC_BASE_URL = os.getenv("ANTHROPIC_BASE_URL")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
correct_password = os.getenv("correct_password")

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

anthropic_client = anthropic.Anthropic(
    api_key=ANTHROPIC_API_KEY,
    base_url=ANTHROPIC_BASE_URL if ANTHROPIC_BASE_URL else None
)

def agent_activate():
    pass

def resume_library():
    pass

user_decision = int(input("\nTo upload your resume to Co-Impact and apply, press 1, \nIf you are a Co-Impact worker press 2: "))
if user_decision == 1:
    agent_activate()

elif user_decision == 2:
    insert_password = True

    while insert_password == True:
        worker_password = input("\nPlease enter your password to access the Library: ").lower()

        if worker_password == correct_password:
            print("Loading Resume's Library...")
            resume_library()
            insert_password = False

        else:
            print("Invalid password. Try again.")

else:
    print("Invalid input. Please enter 1 or 2.")