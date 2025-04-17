from lm_module import handle_llm_query

def handle_interview_query(message):
    message = message.lower()

    if "data science" in message:
        prompt = "How can someone prepare for data science interviews? Include key topics, resources, and tips."
    elif "ai" in message or "artificial intelligence" in message:
        prompt = "How should someone prepare for artificial intelligence interviews? Include common questions and preparation strategies."
    elif "ml" in message or "machine learning" in message:
        prompt = "What’s the best way to prepare for machine learning interviews? Include topics, projects, and tips."
    elif "resume" in message:
        prompt = "How to tailor a resume specifically for data science or ML interviews?"
    else:
        prompt = f"Give some basic interview questions and  interview preparation tips based on this query: {message}"

    return handle_llm_query(prompt)
