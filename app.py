import streamlit as st
from main import chatbot_response, extract_text_from_pdf, set_pdf_context, generate_notes_from_pdf  # Add set_pdf_context

# Set page title
st.title("UniMentor Chatbot")

# Sidebar for extra config (optional)
st.sidebar.title('Model Parameters')
temperature = st.sidebar.slider("Temperature", 0.0, 2.0, 0.7, 0.1)
max_tokens = st.sidebar.slider('Max Tokens', 1, 4096, 256)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state['messages'] = []

if 'loaded_file_type' not in st.session_state:
    st.session_state['loaded_file_type'] = None

# Chat UI: display history
for msg in st.session_state['messages']:
    with st.chat_message(msg['role']):
        st.markdown(msg['content'])

# User input
if prompt := st.chat_input("Ask me anything (e.g., review my resume, summarize pdf)"):
    st.session_state['messages'].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Run chatbot logic
    response = chatbot_response(prompt)
    st.session_state['messages'].append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)

# File Upload (manual button only)
uploaded_file = st.file_uploader("Upload your PDF or Resume", type=["pdf"], label_visibility="collapsed")

if uploaded_file:
    file_bytes = uploaded_file.read()  # ✅ read once
    text = extract_text_from_pdf(file_bytes)  # ✅ pass to function # Assuming extract_text_from_pdf accepts bytes
    set_pdf_context(text)

    # Decide file type based on name
    if "resume" in uploaded_file.name.lower():
        st.session_state['loaded_file_type'] = "resume"
        st.success("✅ Resume uploaded. Type 'review my resume' to get feedback.")
    else:
        st.session_state['loaded_file_type'] = "pdf"
        st.success("✅ PDF uploaded. Type 'summarize this pdf' to get a summary.")

    if st.button("📝 Generate Notes from PDF"):
        notes = generate_notes_from_pdf(file_bytes)
        st.subheader("Generated Notes:")
        st.markdown(notes)