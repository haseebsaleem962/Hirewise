"""
Standalone training script - run this to train the ML model.
Usage: python train_model.py
"""
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ml.dataset_downloader import download_or_generate_dataset
from ml.model_trainer import train_and_evaluate


def main():
    print("=" * 60)
    print("  HIREWISE - MODEL TRAINING")
    print("=" * 60)

    # Step 1: Ensure dataset exists
    print("\nStep 1: Preparing dataset...")
    df = download_or_generate_dataset()
    print(f"  Dataset ready: {len(df)} samples")

    # Step 2: Train models
    print("\nStep 2: Training models...")
    best_model, vectorizer, metrics = train_and_evaluate()

    print("\n" + "=" * 60)
    print("  TRAINING COMPLETE")
    print(f"  Best Model: {metrics['best_model']}")
    print(f"  Test Accuracy: {metrics['all_results'][metrics['best_model']]['test_accuracy']}%")
    print(f"  Test F1-Score: {metrics['all_results'][metrics['best_model']]['test_f1']}%")
    print("=" * 60)


if __name__ == '__main__':
    main()
