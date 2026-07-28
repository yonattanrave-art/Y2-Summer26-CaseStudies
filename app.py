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

def resume_library():
    try:
        response = supabase.table("candidates").select("*").order("created_at", desc=True).execute()
        candidates = response.data
        
        if not candidates:
            print("\nNo candidates found in the library.")
            return

        while True:
            print(f"\n--- Total Candidates: {len(candidates)} ---")
            for i, c in enumerate(candidates, 1):
                print(f"{i}. {c.get('full_name', 'N/A')} - Location: {c.get('location', 'N/A')}")
            
            choice = input("\nEnter the number of the candidate to view their full profile (or press Enter to exit): ").strip()
            
            if not choice:
                break

            if choice.lower() == "exit":
                print("Exiting the candidate libarary.")
                break

            
            if choice.isdigit():
                idx = int(choice)
                if 1 <= idx <= len(candidates):
                    c = candidates[idx - 1]
                    print(f"\n--- Full Profile for Candidate #{idx} ---")
                    print(f"Full Name: {c.get('full_name', 'N/A')}")
                    print(f"Phone: {c.get('phone', 'N/A')}")
                    print(f"Email: {c.get('email', 'N/A')}")
                    print(f"Location: {c.get('location', 'N/A')}")
                    print(f"Skills: {c.get('skills', 'N/A')}")
                    print(f"Languages: {c.get('languages', 'N/A')}")
                    print(f"Education: {c.get('education', 'N/A')}")
                    print(f"Experience: {c.get('experience', 'N/A')}")
                    print(f"Resume Link: {c.get('resume_url', 'N/A')}")
                    print("-" * 40)
                else:
                    print("\nInvalid candidate number. Please try again.")
            else:
                print("\nInvalid input. Please enter a valid number.")

    except Exception as e:
        print(f"Error loading resume library: {e}")

while True:
    user_decision = int(input("\nTo upload your resume to Co-Impact and apply, press 1, \nIf you are a Co-Impact worker press 2: "))

    if user_decision == 1:
        import agent
        user_decision = int(input("\nTo upload your resume to Co-Impact and apply, press 1, \nIf you are a Co-Impact worker press 2: "))
    
    
    elif user_decision == 2:
        insert_password = True

        while insert_password:
            worker_password = input("\nPlease enter your password to access the Library: ").lower()

            if worker_password == "exit":
                print("Exiting the program.")
                insert_password = False


            elif worker_password == correct_password:
                print("Loading Resume's Library...")
                resume_library()
                insert_password = False

            else:
                print("Invalid password. Try again.")


    elif user_decision == "exit":
        break


    else:
        print("Invalid input. Please enter 1 or 2.")

