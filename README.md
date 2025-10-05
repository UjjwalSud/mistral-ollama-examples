# Mistral + Ollama Examples

Streaming examples for running **Mistral** locally with **Ollama**:
- `generate_stream_simple.py`: minimal `/api/generate` streamer
- `chat_with_files.py`: `/api/chat` that ingests **PDF + DOCX + instructions** and streams output

> These examples are designed to be small, readable, and easy to extend.

---

## Prerequisites

1. **Install Ollama**
   - https://ollama.com (download and install)
   - Start the server:
     ```bash
     ollama serve
     ```

2. **Install the Mistral model**
   ```bash
   ollama pull mistral
   ```

3. (Optional) **Explore the REST API via Postman**
   - Collection: *Ollama REST API*  
     Provided by you: https://www.postman.com/postman-student-programs/ollama-api/collection/suc47x8/ollama-rest-api

---

## Python Setup

Use a virtual environment (recommended):

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

If you're not using `requirements.txt`, install directly:
```bash
pip install requests pypdf python-docx
```

---

## Run the examples

### 1) Minimal generate streamer
```bash
python generate_stream_simple.py
```

You should see tokens stream and a final `--- Completed ---` line.

### 2) Chat with PDF + DOCX + Instructions (streaming)
Edit paths inside `chat_with_files.py`:

```python
PDF_PATH = r"F:\path\to\one.pdf"
DOCX_PATH = r"F:\path\to\two.docx"
INSTRUCTIONS_PATH = r"F:\path\to\instructions.txt"
USER_TASK = "Summarize both documents and then produce a unified action plan."
```

Then run:
```bash
python chat_with_files.py
```

---

## How it works

- **Streaming**: Both scripts set `"stream": true` and read the response as **newline-delimited JSON**.  
  - `/api/generate` emits chunks like:
    ```json
    {"response":"He","done":false}
    {"response":"llo","done":false}
    {"done":true}
    ```
  - `/api/chat` emits chunks like:
    ```json
    {"message":{"role":"assistant","content":"..."}, "done":false}
    {"done":true}
    ```

- **Files ingestion (`chat_with_files.py`)**:
  - Extracts text from a **PDF** (`pypdf`) and **DOCX** (`python-docx`).
  - Reads an **instructions** text file.
  - Sends instructions as a **system** message and document text as a **user** message to `/api/chat`.
  - Streams tokens until `done: true`.

- **Context size safety**:
  - Very large files can exceed model context. The script includes a simple **`safe_truncate()`** helper.  
    For production, consider chunking + retrieval (RAG) for better scaling.

---

## Repo structure

```
mistral-ollama-examples/
├─ chat_with_files.py
├─ generate_stream_simple.py
├─ README.md
└─ requirements.txt   # optional, see below
```

### Example `requirements.txt`
```txt
requests
pypdf
python-docx
```

---

## Tips

- If you see the process hang, ensure `ollama serve` is running and that `http://localhost:11434` is reachable.
- For **non-streaming** responses, set `"stream": false` and read `response.json()` normally.
- Want RAG or multi-file ingestion? Add chunking/embeddings + local search, then feed the top-k chunks into `/api/chat`.

---

## License

MIT (or your preferred license)
