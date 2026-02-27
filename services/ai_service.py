from transformers import pipeline
import re

print("Loading AI summarization model...")

# ✅ explicitly specify model (removes warning)
_summarizer = pipeline(
    task="summarization",
    model="sshleifer/distilbart-cnn-12-6",
    device=-1
)

print("AI model loaded.")


# -----------------------------
# Text cleaning
# -----------------------------
def clean_text(text: str) -> str:
    if not text:
        return ""

    text = re.sub(r"[^\x00-\x7F]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\.{2,}", ".", text)

    return text.strip()


# -----------------------------
# Chunking
# -----------------------------
def chunk_text(text: str, max_words: int = 900):
    words = text.split()
    for i in range(0, len(words), max_words):
        yield " ".join(words[i:i + max_words])


# -----------------------------
# Safe summarization call
# -----------------------------
def _summarize(text: str):
    return _summarizer(
        text,
        max_length=130,
        min_length=30,
        do_sample=False,
    )[0]["summary_text"]


# -----------------------------
# MAIN FUNCTION
# -----------------------------
def generate_summary(text: str) -> str:
    if not text or len(text.strip()) < 50:
        return text

    cleaned = clean_text(text)
    chunks = list(chunk_text(cleaned))

    partial_summaries = []

    for chunk in chunks:
        try:
            partial_summaries.append(_summarize(chunk))
        except Exception as e:
            print(f"AI chunk failed: {e}")

    if not partial_summaries:
        return ""

    combined = " ".join(partial_summaries)

    try:
        final = _summarizer(
            combined,
            max_length=160,
            min_length=40,
            do_sample=False,
        )[0]["summary_text"]
    except Exception:
        final = combined

    return final.strip()