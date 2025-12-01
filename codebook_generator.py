import os
from openai import OpenAI

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_URL = "https://openrouter.ai/api/v1"
FREE_MODEL = "x-ai/grok-4.1-fast:free" 


def write_to_file(filename: str, content: str):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Successfully wrote output to {filename}")
    except IOError as e:
        print(f"ERROR: Could not write to file {filename}. Reason: {e}")


def get_client(system_prompt: str, user_prompt: str) -> str:
    
    client = OpenAI(
        api_key=OPENROUTER_API_KEY,
        base_url=OPENROUTER_URL,
    )
    
    print(f"--- Making API Call to {FREE_MODEL} ---")
    
    response = client.chat.completions.create(
        model=FREE_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.05,
    )
    
    return response.choices[0].message.content


def load_posts_content() -> str:
    try:
        with open('posts.txt', 'r') as f:
            return f.read()
    except FileNotFoundError:
        print("WARNING: 'posts.txt' not found. Using empty content.")
        return ""



def generate_codebook(posts_content: str) -> str:
    
    system_prompt = f"""
    Act as a qualitative researcher analyzing the following Reddit posts. Your task is to develop a **Codebook** based on an open coding process.

    **STRICT OUTPUT INSTRUCTION:** Provide ONLY the codebook content below. Do not include any introductory or concluding conversational text.

    Format the output as a structured hierarchical list using the following Markdown format for each code:

    ### Code Family: [Theme Name]
    - **Code Name:** [Name]
      - **Definition:** [Concise Definition]
      - **Inclusion Criteria:** [When to use this code]
      - **Key Words:** [Words or phrases frequently found in this code]
      - **Example:** [Quote from data]
    """
    
    user_prompt = f"""
    Here is the data for analysis:

    {posts_content}
    """
    
    return get_client(system_prompt, user_prompt)



def classify_posts(codebook: str, posts_content: str) -> str:
    
    system_prompt = f"""
    You are a highly meticulous qualitative data coder. Your task is to process the raw POSTS CONTENT by applying the codes defined in the CODEBOOK. 
    
    Your analysis must maintain the focus on:
    1. **Adult Retrospection:** The lasting effects and consequences of past bullying.
    2. **Current Student Perception:** The immediate feelings, and perception of the bullying situation.

    **STRICT OUTPUT INSTRUCTION:** You must output a single, raw text report that iterates through **EVERY SINGLE POST** in the provided content.

    
    Then, for every post, you must use the following format. If a post is not relevant, you must still output the 'post url:' line and simply state 'No codes applied.' below it.

    **REQUIRED POST FORMAT:**
    
    Post URL: [The URL for the post]
    Code applied: [Exact Specific Code Name from the Codebook]
    Reason: [A concise, specific justification for applying the code as well as a quotation from the post]
    Code applied: [Another Exact Specific Code Name if applicable]
    Reason: [A concise, specific justification for applying the code as well as a quotation from the post]
    ...
    
    Ensure you use the exact CODE NAMES from the CODEBOOK.
    
    """
    
    user_prompt = f"""
    Please apply the following Codebook to the provided Posts Content and generate the Detailed Classification Report in the specified format, including a reason for every code applied.

    CODEBOOK:
    {codebook}

    POSTS CONTENT:
    {posts_content}
    """
    
    return get_client(system_prompt, user_prompt)

# --- Step 3: Analytical Summary  ---

def generate_summary(codebook: str, classification_report: str) -> str:

    system_prompt = f"""
    Act as a senior qualitative data analyst. Your first task is to **meticulously count and aggregate** the data in the provided CLASSIFICATION REPORT. Your second task is to use those counts and the CODEBOOK to produce a structured, comprehensive **Analytical Summary**.

    **COUNTING & REPORTING INSTRUCTIONS (CRITICAL):**
    1.  Count the **Total Posts Analyzed** (count of 'post url:' lines).
    2.  Count the **Total Posts Classified** (Total Posts Analyzed minus the count of 'No codes applied.' lines).
    3.  Count the frequency of **EVERY SINGLE Code Name** used in the report (count of 'code applied: [Code Name]' lines).
    4.  List the codes and their counts from highest to lowest frequency.

    **SUMMARY GENERATION INSTRUCTIONS:**
    * The analysis must focus on connecting the code frequencies to the central themes: **Adult Retrospection** and **Current Student Perception**.
    * The final output must strictly follow the Markdown structure below, incorporating the counts you calculated in Section 1.

    **STRICT OUTPUT INSTRUCTION:** Provide ONLY the content for the analytical summary, using the Markdown headings specified below. Do not include any introductory or concluding conversational text.
    
    ### 1. Key Statistics and Code Frequency
    * **Total Posts Analyzed:** [Your calculated count]
    * **Total Posts Classified:** [Your calculated count]
    * **Full Code Frequency List:** (List ALL codes and their exact counts, sorted high to low, one entry per line)

    ### 2. Thematic Interpretation
    (Provide a concise, insightful paragraph for the top three most frequent Codes/Code Families, interpreting what this frequency suggests about the lasting effects (Adult Retrospection) and/or immediate experience (Current Student Perception) of bullying.)
    
    ### 3. Conclusion and Key Takeaways
    (Summarize the core finding in one to two sentences. Identify a maximum of two specific, actionable insights or suggestions for further research based on the strongest patterns.)
    """
    
    user_prompt = f"""
    Please perform the counting task on the CLASSIFICATION REPORT and then generate the Analytical Summary based on the CODEBOOK and your calculated counts.

    CODEBOOK:
    {codebook}

    CLASSIFICATION REPORT:
    {classification_report}
    """
    
    return get_client(system_prompt, user_prompt)

# --- Main Execution ---

def main():    
    try:
        POSTS_CONTENT = load_posts_content()
        
        print(f"Starting OpenRouter analysis pipeline using the free model: {FREE_MODEL} (Minimal Implementation).")

        print("\n\n=== Executing Step 1: Generating Codebook ===")
        codebook_output = generate_codebook(POSTS_CONTENT)
        print("\n\n=============== STEP 1: GENERATED CODEBOOK ===============\n")
        write_to_file("1_codebook.txt", codebook_output)
        
        print("\n\n=== Executing Step 2: Classifying Posts ===")
        classification_output = classify_posts(codebook_output, POSTS_CONTENT)
        print("\n\n=============== STEP 2: POST CLASSIFICATION REPORT ===============\n")
        write_to_file("2_classification_report.txt", classification_output)
        
        print("\n\n=== Executing Step 3: Generating Summary ===")
        summary_output = generate_summary(codebook_output, classification_output)
        print("\n\n=============== STEP 3: ANALYTICAL SUMMARY ===============\n")
        write_to_file("3_analytical_summary.txt", summary_output)
        print("\n\n======================================================\n")
        print("Pipeline Complete. Review the outputs above and the new files created.")
        
    except Exception as e:
        print(f"\n\nFATAL ERROR DURING EXECUTION: {e}")
        print("The program terminated due to an error.")


if __name__ == "__main__":
    main()