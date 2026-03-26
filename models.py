from transformers import pipeline

print("Loading fake news model...")
fake_news_clf = pipeline(
    "text-classification",
    model="jy46604790/Fake-News-Bert-Detect"
)

print("Loading financial sentiment model...")
sentiment_clf = pipeline(
    "text-classification",
    model="ProsusAI/finbert"
)

print("Loading NER model...")
ner_clf = pipeline(
    "ner",
    model="dslim/bert-base-NER",
    aggregation_strategy="simple"
)

print("Loading event classifier (zero-shot)...")
event_clf = pipeline(
    "zero-shot-classification",
    model="facebook/bart-large-mnli"
)

print("Loading stance detector...")
stance_clf = pipeline(
    "zero-shot-classification",
    model="facebook/bart-large-mnli"
)

print("All models loaded successfully.")