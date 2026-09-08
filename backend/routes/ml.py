"""
ML routes - trigger model training and get model status/metrics.
"""
import threading
from flask import Blueprint, jsonify
from ml.classifier import get_model_status, get_model_metrics

ml_bp = Blueprint('ml', __name__)

_training_in_progress = False


@ml_bp.route('/train', methods=['POST'])
def trigger_training():
    """Trigger model re-training in background."""
    global _training_in_progress

    if _training_in_progress:
        return jsonify({'message': 'Training already in progress'}), 409

    def train_in_background():
        global _training_in_progress
        _training_in_progress = True
        try:
            from ml.model_trainer import train_and_evaluate
            train_and_evaluate()
        except Exception as e:
            print(f"Training error: {e}")
        finally:
            _training_in_progress = False

    thread = threading.Thread(target=train_in_background)
    thread.start()

    return jsonify({
        'message': 'Model training started in background. Check /api/ml/status for progress.'
    }), 202


@ml_bp.route('/status', methods=['GET'])
def model_status():
    """Get model status."""
    status = get_model_status()
    status['training_in_progress'] = _training_in_progress
    return jsonify(status), 200


@ml_bp.route('/metrics', methods=['GET'])
def model_metrics():
    """Get detailed model evaluation metrics."""
    metrics = get_model_metrics()
    if not metrics:
        return jsonify({'error': 'No metrics available. Train the model first.'}), 404
    return jsonify(metrics), 200
