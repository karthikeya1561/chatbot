from advisor_module import handle_academic_query
from career_module import handle_career_query, handle_resume_query
from interview_module import handle_interview_query
from pdf_summary_module import extract_text_from_pdf, summarize_pdf, generate_notes_from_pdf
from lm_module import handle_llm_query, set_pdf_context

# Global state
last_domain = None
loaded_file_path = None
loaded_file_type = None
last_llm_topic = None
user_interest_field = None
project_suggested_once = False
resume_outline_pending = False 


def chatbot_response(message):
    global last_domain, loaded_file_path, loaded_file_type
    global last_llm_topic, user_interest_field, project_suggested_once, resume_outline_pending

    message = message.lower().strip()

    # Reset topic if unrelated to projects
    if any(kw in message for kw in ["timetable", "schedule", "backlog", "resume", "interview", "pdf"]):
        last_llm_topic = None
        user_interest_field = None

    # Basic greetings
    if message in ["hello", "hi", "hey"]:
        return "Hey there! 😊 How can I help you today?"
    elif "thank" in message:
        return "You're welcome! 😊"
    elif message in ["bye", "goodbye"]:
        return "Goodbye! Have a great day!"
    elif "how are you" in message:
        return "I'm just code, but I'm running great! 😄"

    # PDF Upload
    if "upload pdf" in message:
        file_path = input("Enter PDF file path: ")
        pdf_text = extract_text_from_pdf(file_path)
        set_pdf_context(pdf_text)
        loaded_file_path = file_path
        loaded_file_type = "pdf"
        return "✅ PDF uploaded successfully."

    # Resume Upload
    elif "upload resume" in message:
        file_path = input("Enter resume file path: ")
        if file_path.endswith(".pdf"):
            resume_text = extract_text_from_pdf(file_path)
            set_pdf_context(resume_text)
            loaded_file_path = file_path
            loaded_file_type = "resume"
            return "✅ Resume uploaded. Type 'review my resume' to get feedback."
        else:
            return "⚠️ Please upload a valid PDF file for your resume."

    # ✅ Review Resume (more specific)
    elif "review" in message and "resume" in message:
        from pdf_summary_module import cached_text
        if not cached_text.strip():
            return "❌ Please upload your resume first."
        return handle_llm_query("Can you review this resume for clarity, formatting, and impact?")

    # ✅ Resume Tips, Format, or General
    elif "resume" in message:
        response = handle_resume_query(message)
        if "generate a resume outline" in response.lower():
            resume_outline_pending = True   # ➕ Track user said yes
        return response


    # Summarize PDF
    elif "summarize pdf" in message:
        from pdf_summary_module import cached_text
        if not cached_text.strip():
            return "❌ Please upload a PDF first."
        return summarize_pdf()
    
    # Generate Notes
    elif "generate notes" in message:
        from pdf_summary_module import cached_text
        if not cached_text.strip():
            return "❌ Please upload a PDF first."
        return generate_notes_from_pdf(cached_text)

    # Academic Queries
    elif "academic" in message or "subject" in message:
        return handle_academic_query(message, last_domain)

    # Career Queries
    elif "career" in message or "job" in message or "roadmap" in message or last_domain == "career":
        fields = ["ai", "ml", "mechanical", "civil", "electrical", "computer science", "psychology", "biology"]
        
        # If the user provides their interest (like "ai") after asking about careers
        for field in fields:
            if field in message:
                last_domain = None  # Reset the context after use
                return handle_llm_query(f"Suggest some career paths for someone interested in {field}")

        # If it's the initial request for career guidance
        response, last_domain = handle_career_query(message, last_domain)
        return response

    # Interview Queries
    elif "interview" in message:
        return handle_interview_query(message)

    # Project Queries
    elif "project" in message:
        last_llm_topic = "projects"
        if project_suggested_once:
            return "✅ I've already shared project ideas. Ask anything else or say 'more projects' for more ideas."
        if user_interest_field:
            project_suggested_once = True
            return handle_llm_query(f"Suggest academic project ideas in {user_interest_field} with real-world relevance.")
        return "🧠 What field are you interested in? (e.g., computer science, electrical, mechanical)"

    # Handling project interest after asking field
    elif last_llm_topic == "projects":
        fields = ["computer science", "electrical", "mechanical", "civil", "biology", "psychology", "ai", "ml"]
        for field in fields:
            if field in message:
                user_interest_field = field
                project_suggested_once = True
                last_llm_topic = None  # ✅ Reset project mode after suggestion
                return handle_llm_query(f"Suggest academic project ideas in {field} with real-world relevance.")
        return "🔍 Please mention a valid field (e.g., computer science, electrical, mechanical)."

    # Timetable & Backlog
    elif "timetable" in message or "schedule" in message:
        return handle_llm_query(f"Create a personalized timetable based on this query: {message}")
    elif "backlog" in message:
        return handle_llm_query(f"Help me plan and clear academic backlogs. Query: {message}")

    elif resume_outline_pending and message in ["yes", "yeah", "please do", "go ahead", "okay"]:
        resume_outline_pending = False
        return (
            "Here’s a simple resume outline you can use:\n"
            "1. **Name & Contact Info**\n"
            "2. **Professional Summary**\n"
            "3. **Skills** (technical & soft)\n"
            "4. **Projects** (title, tech stack, what you did)\n"
            "5. **Internships or Experience**\n"
            "6. **Education**\n"
            "7. **Certifications or Achievements**\n\n"
            "Let me know if you want help filling it in!"
        )

    
    # Default Fallback
    return handle_llm_query(message)


def main():
    print("Welcome to Smart ChatBot! (type 'exit' to quit)")
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            print("Chatbot: Goodbye!")
            break
        print("Chatbot:", chatbot_response(user_input))

if __name__ == "__main__":
    main()
