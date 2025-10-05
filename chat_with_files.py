import os
import json
import requests
from pypdf import PdfReader          # pip install pypdf
from docx import Document            # pip install python-docx

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "mistral"  # change if you like

# ---------- helpers to extract text ----------
def extract_text_from_pdf(path: str) -> str:
    reader = PdfReader(path)
    parts = []
    for page in reader.pages:
        txt = page.extract_text() or ""
        parts.append(txt)
    return "\n".join(parts)

def extract_text_from_docx(path: str) -> str:
    doc = Document(path)
    return "\n".join(p.text for p in doc.paragraphs)

def read_text_file(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

# (Optional) simple truncation to protect context length
def safe_truncate(text: str, max_chars: int = 120_000) -> str:
    return text if len(text) <= max_chars else text[:max_chars] + "\n\n...[truncated]..."

# ---------- main call ----------
def stream_chat_with_files(pdf_path: str, docx_path: str, instructions_path: str, user_task: str):
    # 1) Load sources
    pdf_text = extract_text_from_pdf(pdf_path)
    docx_text = extract_text_from_docx(docx_path)
    instructions_text = read_text_file(instructions_path)

    # 2) (Optional) truncate to avoid blowing past model context
    pdf_text = safe_truncate(pdf_text)
    docx_text = safe_truncate(docx_text)
    instructions_text = safe_truncate(instructions_text, 30_000)

    # 3) Build messages for /api/chat
    messages = [
        {
            "role": "system",
            "content": (
                "You are a precise assistant. Follow the instructions provided below strictly.\n\n"
                "=== INSTRUCTIONS START ===\n"
                f"{instructions_text}\n"
                "=== INSTRUCTIONS END ==="
            )
        },
        {
            "role": "user",
            "content": (
                f"Task: {user_task}\n\n"
                "You are given two documents as context.\n\n"
                "=== PDF CONTENT START ===\n"
                f"{pdf_text}\n"
                "=== PDF CONTENT END ===\n\n"
                "=== DOCX CONTENT START ===\n"
                f"{docx_text}\n"
                "=== DOCX CONTENT END ===\n\n"
                "Now produce your answer."
            )
        }
    ]

    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": True,
    }

    # 4) Stream from Ollama
    with requests.post(OLLAMA_URL, json=payload, stream=True) as r:
        r.raise_for_status()
        for line in r.iter_lines(decode_unicode=True):
            if not line:
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue

            # /api/chat stream returns chunks like {"message":{"role":"assistant","content":"..."}, "done":false}
            msg = data.get("message", {})
            chunk = msg.get("content")
            if chunk:
                print(chunk, end="", flush=True)

            if data.get("done"):
                print("\n--- Completed ---")
                break


if __name__ == "__main__":
    # 🔧 Put your file paths and the user task here:
    PDF_PATH = r"C\data\one.pdf"
    DOCX_PATH = r"C\data\two.docx"
    INSTRUCTIONS_PATH = r"C\data\instructions.txt"

    # What you want the model to do with those files + instructions:
    USER_TASK = "Summarize both documents and then produce a unified action plan."

    stream_chat_with_files(PDF_PATH, DOCX_PATH, INSTRUCTIONS_PATH, USER_TASK)
