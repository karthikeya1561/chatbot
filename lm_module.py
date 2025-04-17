import re
from groq import Groq
from pdf_summary_module import get_pdf_page_text

# Replace with your actual key securely in production
client = Groq(api_key="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")

# Global PDF context (either resume or academic PDF)
pdf_context = ""

def set_pdf_context(text):
    global pdf_context
    pdf_context = text

def handle_llm_query(message):
    try:
        system_prompt = "You are a helpful university assistant chatbot."

        # 📄 Check if the user is referring to a specific page
        page_match = re.search(r'page\s+(\d+)', message.lower())
        if page_match:
            page_num = int(page_match.group(1))
            page_text = get_pdf_page_text(page_num)
            if "❌" not in page_text:
                system_prompt += f"\nRefer to this PDF page content:\n'''{page_text}'''"
                
        # Only include PDF if user asks about it or mentions something related
        relevant_keywords = ["pdf", "resume", "cv", "speech", "transcript", "document"]
        if any(keyword in message.lower() for keyword in relevant_keywords):
            system_prompt += f"\nRefer to this PDF content:\n'''{pdf_context[:2000]}'''"


        # 💬 Chat completion
        chat_completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ]
        )

        return chat_completion.choices[0].message.content.strip()

    except Exception as e:
        return f"❌ Groq API Error: {str(e)}"
