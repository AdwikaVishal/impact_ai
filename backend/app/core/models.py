"""Migrated from root models.py - ML pipelines"""
from transformers import pipeline

# Global models (lazy load in prod)
_models = {}

def get_model(model_name):
    if model_name not in _models:
        if model_name == "fake_news":
            _models[model_name] = pipeline("text-classification", model="jy46604790/Fake-News-Bert-Detect")
        elif model_name == "sentiment":
            _models[model_name] = pipeline("text-classification", model="ProsusAI/finbert")
        # Add others...
    return _models[model_name]

