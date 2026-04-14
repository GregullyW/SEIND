import re
import unicodedata

def normalize_text(text):
    if not isinstance(text, str):
        text = str(text)

    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("utf-8")

    text = text.lower()

    text = text.strip()

    text = re.sub(r"[^a-z0-9\s]", "", text)

    text = re.sub(r"\s+", " ", text)

    return text

def detect_separator(path, n_lines=5):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        sample = "".join([f.readline() for _ in range(n_lines)])

    candidates = [",", ";", "\t", "|"]

    return max(candidates, key=sample.count)