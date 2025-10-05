import json
import requests

URL = "http://localhost:11434/api/generate"

def stream_generate(model: str, prompt: str):
    payload = {"model": model, "prompt": prompt, "stream": True}
    with requests.post(URL, json=payload, stream=True) as r:
        r.raise_for_status()
        for line in r.iter_lines(decode_unicode=True):
            if not line:
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue

            if "response" in data and data["response"] is not None:
                print(data["response"], end="", flush=True)

            if data.get("done"):
                print("\n--- Completed ---")
                break

if __name__ == "__main__":
    stream_generate("mistral", "Give me 3 bullet points about Rust vs Go.")
