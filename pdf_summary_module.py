import fitz  # PyMuPDF
import re
from transformers import pipeline, BartTokenizerFast
from tqdm import tqdm
import torch
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from io import BytesIO

# Load summarization model
device = 0 if torch.cuda.is_available() else -1
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6", device=device)
tokenizer = BartTokenizerFast.from_pretrained("sshleifer/distilbart-cnn-12-6", add_prefix_space=True)

# Global cache
cached_pages = {}
cached_text = ""

# ========== TEXT EXTRACTION ==========

def extract_text_from_pdf(file_bytes):
    global cached_pages, cached_text
    cached_pages.clear()
    cached_text = ""

    file_stream = BytesIO(file_bytes)
    doc = fitz.open(stream=file_stream, filetype="pdf")
    for i, page in enumerate(tqdm(doc, desc="📄 Extracting text")):
        page_text = page.get_text()
        cached_pages[i + 1] = page_text.strip()
        cached_text += page_text + "\n"

    return cached_text

# ========== SUMMARIZATION HELPERS ==========

def split_text_by_tokens(paragraphs, max_tokens=1024):
    chunks = []
    current_chunk = ""
    for para in paragraphs:
        current_tokens = tokenizer.tokenize(current_chunk)
        para_tokens = tokenizer.tokenize(para)
        if len(current_tokens) + len(para_tokens) <= max_tokens:
            current_chunk += " " + para
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = para
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

def extract_heading(text):
    lines = text.strip().split('\n')
    first_line = lines[0]
    return re.sub(r'[^a-zA-Z0-9\s]', '', first_line).strip().title()

# ========== MAIN SUMMARIZATION ==========

def summarize_text(paragraphs):
    chunks = split_text_by_tokens(paragraphs)
    final_output = ""
    for i, chunk in enumerate(tqdm(chunks, desc="🧠 Summarizing")):
        summary = summarizer(chunk, max_length=250, min_length=30, do_sample=False)[0]['summary_text']
        summary_sentences = re.split(r'(?<=[.!?]) +', summary)
        topic_title = extract_heading(chunk) or f"Topic {i+1}"
        final_output += f"\n{topic_title}:\n"
        for sentence in summary_sentences:
            if sentence.strip():
                final_output += f"- {sentence.strip()}\n"
        if summary_sentences:
            explanation = " ".join(summary_sentences[:2])
            final_output += f"\n{explanation.strip()}\n"
    return final_output.strip()

def summarize_pdf(pdf_text):
    if not pdf_text:
        return "❌ PDF not uploaded or empty."
    paragraphs = [p.strip() for p in pdf_text.split('\n\n') if len(p.strip()) > 40]
    return summarize_text(paragraphs)

# ========== NOTES GENERATION ==========

def generate_notes_from_pdf(input_data):
    if isinstance(input_data, bytes):  # Case: file bytes from uploader
        doc = fitz.open(stream=BytesIO(input_data), filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
    elif isinstance(input_data, str):  # Case: cached_text
        text = input_data
    else:
        return "❌ Invalid input format for notes generation."

    paragraphs = text.split('\n\n')
    clean_paragraphs = [p.strip().replace('\n', ' ') for p in paragraphs if len(p.strip()) > 40]

    if not clean_paragraphs:
        return "Couldn't extract meaningful content for notes."

    vectorizer = TfidfVectorizer(stop_words='english')
    X = vectorizer.fit_transform(clean_paragraphs)
    scores = np.asarray(X.sum(axis=1)).ravel()

    top_indices = scores.argsort()[-8:][::-1]
    notes = [f"• {clean_paragraphs[i]}" for i in top_indices]

    return "\n".join(notes)

# ========== PAGE-WISE VIEW ==========

def get_pdf_page_text(page_num):
    if not cached_pages:
        return "❌ No PDF loaded."
    return cached_pages.get(page_num, f"❌ Page {page_num} not found.")
