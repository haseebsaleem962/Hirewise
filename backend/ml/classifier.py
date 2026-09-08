"""
Resume classifier - loads trained model and predicts resume categories.
"""
import os
import json
import pickle
import numpy as np

from ml.preprocessor import preprocess_for_classification

MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models')

_model = None
_vectorizer = None
_categories = None


def load_model():
    """Load the trained model, vectorizer, and categories."""
    global _model, _vectorizer, _categories

    if _model is not None:
        return _model, _vectorizer, _categories

    model_path = os.path.join(MODEL_DIR, 'resume_classifier.pkl')
    vectorizer_path = os.path.join(MODEL_DIR, 'tfidf_vectorizer.pkl')
    categories_path = os.path.join(MODEL_DIR, 'categories.json')

    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"Model not found at {model_path}. Please train the model first."
        )

    with open(model_path, 'rb') as f:
        _model = pickle.load(f)

    with open(vectorizer_path, 'rb') as f:
        _vectorizer = pickle.load(f)

    with open(categories_path, 'r') as f:
        _categories = json.load(f)

    return _model, _vectorizer, _categories


def predict_category(resume_text):
    """
    Predict the category of a resume.
    Returns: (category, confidence_score)
    """
    model, vectorizer, categories = load_model()

    processed = preprocess_for_classification(resume_text)
    features = vectorizer.transform([processed])

    prediction = model.predict(features)[0]
    confidence = 0.0

    if hasattr(model, 'predict_proba'):
        probs = model.predict_proba(features)[0]
        confidence = float(np.max(probs)) * 100
    elif hasattr(model, 'decision_function'):
        scores = model.decision_function(features)[0]
        confidence = float(np.max(scores)) * 100

    return prediction, round(confidence, 2)


def get_category_probabilities(resume_text):
    """
    Get probability distribution across all categories.
    Returns: dict of {category: probability_percentage}
    """
    model, vectorizer, categories = load_model()

    processed = preprocess_for_classification(resume_text)
    features = vectorizer.transform([processed])

    if hasattr(model, 'predict_proba'):
        probs = model.predict_proba(features)[0]
        return {cat: round(float(p) * 100, 2) for cat, p in zip(categories, probs)}
    else:
        # For models without predict_proba, return binary
        prediction = model.predict(features)[0]
        return {cat: (100.0 if cat == prediction else 0.0) for cat in categories}


def get_model_status():
    """Check if model is trained and available."""
    model_path = os.path.join(MODEL_DIR, 'resume_classifier.pkl')
    metrics_path = os.path.join(MODEL_DIR, 'model_metrics.json')

    if not os.path.exists(model_path):
        return {'trained': False, 'message': 'Model not trained yet'}

    status = {'trained': True}

    if os.path.exists(metrics_path):
        with open(metrics_path, 'r') as f:
            metrics = json.load(f)
        status['best_model'] = metrics.get('best_model', 'Unknown')
        status['accuracy'] = metrics.get('all_results', {}).get(
            metrics.get('best_model', ''), {}
        ).get('test_accuracy', 0)
        status['categories'] = metrics.get('categories', [])
        status['total_samples'] = metrics.get('total_samples', 0)

    import time
    status['last_trained'] = time.ctime(os.path.getmtime(model_path))

    return status


def get_model_metrics():
    """Get detailed model evaluation metrics."""
    metrics_path = os.path.join(MODEL_DIR, 'model_metrics.json')

    if not os.path.exists(metrics_path):
        return None

    with open(metrics_path, 'r') as f:
        return json.load(f)
