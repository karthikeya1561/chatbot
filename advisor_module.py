from lm_module import handle_llm_query  # make sure this import is there

def handle_academic_query(message, last_domain):
    prompt = f"""The user has an academic concern. Based on the message below, give helpful advice, course suggestions, or study tips.
If the user mentions a domain like AI, mechanical, etc., suggest 2-3 relevant subjects.
If it's about backlogs, scheduling, or timetables, offer motivating and practical advice.

User message: {message}
"""
    response = handle_llm_query(prompt)
    return response, last_domain
