"""
Model trainer for resume classification.
Trains and evaluates multiple ML models, selects the best one.
"""
import os
import json
import pickle
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix
)

from ml.preprocessor import preprocess_for_classification

MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models')
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')


def load_dataset(data_path=None):
    """Load the resume dataset."""
    if data_path is None:
        data_path = os.path.join(DATA_DIR, 'resume_dataset.csv')

    if not os.path.exists(data_path):
        from ml.dataset_downloader import download_or_generate_dataset
        df = download_or_generate_dataset(data_path)
    else:
        df = pd.read_csv(data_path)

    return df


def train_and_evaluate(data_path=None):
    """Train multiple models and select the best one."""
    os.makedirs(MODEL_DIR, exist_ok=True)

    print("=" * 60)
    print("RESUME CLASSIFIER - TRAINING PIPELINE")
    print("=" * 60)

    # Load dataset
    print("\n[1/5] Loading dataset...")
    df = load_dataset(data_path)
    print(f"  Total samples: {len(df)}")
    print(f"  Categories: {df['category'].nunique()}")
    print(f"  Category distribution:\n{df['category'].value_counts().to_string()}")

    # Preprocess text
    print("\n[2/5] Preprocessing text...")
    df['processed_text'] = df['resume_text'].apply(preprocess_for_classification)

    # Feature extraction with TF-IDF
    print("\n[3/5] Extracting features (TF-IDF)...")
    tfidf = TfidfVectorizer(
        max_features=5000,
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.95,
        sublinear_tf=True
    )
    X = tfidf.fit_transform(df['processed_text'])
    y = df['category']

    # Split: 70% train, 15% validation, 15% test
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=0.30, random_state=42, stratify=y
    )
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.50, random_state=42, stratify=y_temp
    )

    print(f"  Train: {X_train.shape[0]}, Validation: {X_val.shape[0]}, Test: {X_test.shape[0]}")

    # Define models to compare
    models = {
        'Logistic Regression': LogisticRegression(max_iter=1000, C=1.0, random_state=42),
        'Naive Bayes': MultinomialNB(alpha=0.1),
        'Random Forest': RandomForestClassifier(n_estimators=200, max_depth=None, random_state=42),
        'SVM': SVC(kernel='linear', C=1.0, probability=True, random_state=42)
    }

    # Train and evaluate each model
    print("\n[4/5] Training and evaluating models...")
    results = {}
    trained_models = {}

    for name, model in models.items():
        print(f"\n  Training {name}...")
        model.fit(X_train, y_train)

        # Validate
        val_pred = model.predict(X_val)
        val_acc = accuracy_score(y_val, val_pred)
        val_f1 = f1_score(y_val, val_pred, average='weighted')

        # Test
        test_pred = model.predict(X_test)
        test_acc = accuracy_score(y_test, test_pred)
        test_prec = precision_score(y_test, test_pred, average='weighted')
        test_rec = recall_score(y_test, test_pred, average='weighted')
        test_f1 = f1_score(y_test, test_pred, average='weighted')

        results[name] = {
            'val_accuracy': round(val_acc * 100, 2),
            'val_f1': round(val_f1 * 100, 2),
            'test_accuracy': round(test_acc * 100, 2),
            'test_precision': round(test_prec * 100, 2),
            'test_recall': round(test_rec * 100, 2),
            'test_f1': round(test_f1 * 100, 2)
        }

        trained_models[name] = model

        print(f"    Val Accuracy: {val_acc*100:.2f}% | Val F1: {val_f1*100:.2f}%")
        print(f"    Test Accuracy: {test_acc*100:.2f}% | Test F1: {test_f1*100:.2f}%")

    # Select best model based on validation F1
    best_model_name = max(results, key=lambda k: results[k]['val_f1'])
    best_model = trained_models[best_model_name]

    print(f"\n{'=' * 60}")
    print(f"  BEST MODEL: {best_model_name}")
    print(f"  Test Accuracy: {results[best_model_name]['test_accuracy']}%")
    print(f"  Test F1-Score: {results[best_model_name]['test_f1']}%")
    print(f"{'=' * 60}")

    # Detailed classification report for best model
    print("\n[5/5] Detailed Classification Report (Best Model):")
    test_pred = best_model.predict(X_test)
    print(classification_report(y_test, test_pred, zero_division=0))

    # Confusion matrix
    cm = confusion_matrix(y_test, test_pred, labels=best_model.classes_)
    print("\nConfusion Matrix:")
    print(cm)

    # Save best model and vectorizer
    model_path = os.path.join(MODEL_DIR, 'resume_classifier.pkl')
    vectorizer_path = os.path.join(MODEL_DIR, 'tfidf_vectorizer.pkl')
    metrics_path = os.path.join(MODEL_DIR, 'model_metrics.json')
    categories_path = os.path.join(MODEL_DIR, 'categories.json')

    with open(model_path, 'wb') as f:
        pickle.dump(best_model, f)
    print(f"\nModel saved to: {model_path}")

    with open(vectorizer_path, 'wb') as f:
        pickle.dump(tfidf, f)
    print(f"Vectorizer saved to: {vectorizer_path}")

    # Save categories
    categories = sorted(df['category'].unique().tolist())
    with open(categories_path, 'w') as f:
        json.dump(categories, f)

    # Save metrics
    metrics = {
        'best_model': best_model_name,
        'all_results': results,
        'classification_report': classification_report(
            y_test, test_pred, output_dict=True, zero_division=0
        ),
        'confusion_matrix': cm.tolist(),
        'categories': categories,
        'train_samples': X_train.shape[0],
        'val_samples': X_val.shape[0],
        'test_samples': X_test.shape[0],
        'total_samples': len(df)
    }
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f, indent=2)
    print(f"Metrics saved to: {metrics_path}")

    return best_model, tfidf, metrics


if __name__ == '__main__':
    train_and_evaluate()
