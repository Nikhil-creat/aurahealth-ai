"""CNN + RAG food scan. Swap `classify` for a fine-tuned Food-101 model (ResNet/EfficientNet)."""
import io, os
from PIL import Image

def classify(img: Image.Image):
    """Stub -> (label, confidence, grams). Replace with torch inference:
    model(preprocess(img)).softmax(-1); grams from a plate-ratio/depth regressor."""
    w, h = img.size
    return "dal", 0.5, round(min(400, 150 + (w * h) / 20000))

def rag_lookup(label: str, k: int = 3):
    import chromadb
    c = chromadb.HttpClient(host=os.getenv("CHROMA_HOST", "chroma"), port=8000)
    return c.get_or_create_collection("nutrition_facts").query(query_texts=[label], n_results=k)

def scan(data: bytes, eat: set[str], avoid: set[str]):
    label, conf, grams = classify(Image.open(io.BytesIO(data)).convert("RGB"))
    try: facts = rag_lookup(label)["documents"][0]
    except Exception: facts = []
    l = label.lower()
    verdict = "avoid" if any(a.lower() in l for a in avoid) else "ok" if any(e.lower() in l for e in eat) else "unknown"
    return {"label": label, "confidence": conf, "portion_g": grams, "facts": facts, "verdict": verdict}
