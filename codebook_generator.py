import google.generativeai as genai
import os
import time

### CONFIGURATION: ENTER YOUR API KEY
API_KEY = "" 
MODEL = 'gemini-2.0-flash-lite'

def generate(model, prompt, max_retries=10):
    last_exception = None
    for attempt in range(1,max_retries+1):
        try:
            return model.generate_content(prompt)
        except Exception as e:
            last_exception = e
            
            wait_time = attempt * 15
            
            print(f"\n[Retry] Error encountered: {e}")
            print(f"\nAttempt: {attempt}/{max_retries}")
            print(f"\nWaiting: {wait_time} seconds...")
            
            time.sleep(wait_time)
    
    if last_exception:
        raise last_exception

def run_gemini():
    if not API_KEY:
        print("Error: API_KEY is empty. Please set your Google Gemini API key within the script.")
        return
    try:
        genai.configure(api_key=API_KEY)

        model = genai.GenerativeModel(MODEL)

        file_path = 'posts.txt'
        
        if not os.path.exists(file_path):
            print(f"Error: '{file_path}' not found. Please make sure the file is in the same folder.")
            return

        with open(file_path, 'r', encoding='utf-8') as file:
            file_content = file.read()

        prompt = (
            "Act as a qualitative researcher analyzing the following Reddit posts. "
            "Your task is to develop a **Preliminary Codebook** based on an open coding process.\n\n"
            "**STRICT OUTPUT INSTRUCTION:** Provide ONLY the codebook content below. Do not include any introductory or concluding conversational text.\n\n"
            "Format the output as a structured hierarchical list using the following format for each code:\n\n"
            "### Theme: [Theme Name]\n"
            "- **Code Name:** [Name]\n"
            "  - **Definition:** [Concise Definition]\n"
            "  - **Inclusion Criteria:** [When to use this code]\n"
            "  - **Exclusion Criteria:** [When NOT to use this code]\n"
            "  - **Example:** [Quote from data]\n\n"
            "Here is the data:\n\n"
            f"{file_content}"
        )

        print(f"Read {len(file_content)} characters from '{file_path}'.")
        print(f"Sending to {MODEL} for Qualitative Code Development...")
        
        response = generate(model, prompt)

        output_filename = 'codebook.txt'
        with open(output_filename, 'w', encoding='utf-8') as out_file:
            out_file.write(response.text)

        print(f"Preliminary Codebook successfully written to '{output_filename}'")

    except Exception as e:
        print(e)

if __name__ == "__main__":
    run_gemini()