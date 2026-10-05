"""
ML classification service — trains and uses ML models to classify
resume-JD match quality. Includes SHAP-based explainability.
"""

import os
import logging
import json
from typing import Dict, List, Any, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)

# ── Lazy-loaded model components ─────────────────────────────
_trained_model = None
_model_metadata = None

FEATURE_NAMES = [
    "skill_match",
    "semantic_similarity",
    "experience_match",
    "education_match",
    "project_relevance",
    "ats_score",
    "missing_skill_count",
    "keyword_density",
]

LABEL_MAP = {
    0: "Poor Match",
    1: "Weak Match",
    2: "Moderate Match",
    3: "Strong Match",
}


def engineer_features(
    skill_score: float,
    semantic_score: float,
    experience_score: float,
    education_score: float,
    project_score: float,
    ats_score: float,
    missing_skill_count: int,
    keyword_density: float,
) -> np.ndarray:
    """
    Create a feature vector from analysis component scores.
    All scores are expected on a 0–100 scale (normalized to 0–1).
    """
    features = np.array([
        skill_score / 100.0,
        semantic_score / 100.0,
        experience_score / 100.0,
        education_score / 100.0,
        project_score / 100.0,
        ats_score / 100.0,
        min(missing_skill_count / 20.0, 1.0),  # Normalize to ~0-1
        keyword_density,
    ]).reshape(1, -1)
    return features


def generate_weak_labels(composite_score: float) -> int:
    """
    Generate weak labels from composite score for training.
    IMPORTANT: These are synthetic/weak labels, NOT verified employer decisions.
    """
    if composite_score >= 75:
        return 3  # Strong Match
    elif composite_score >= 50:
        return 2  # Moderate Match
    elif composite_score >= 30:
        return 1  # Weak Match
    else:
        return 0  # Poor Match


def train_models(
    features_list: List[np.ndarray],
    labels: List[int],
    save_dir: str = None,
) -> Dict[str, Any]:
    """
    Train Logistic Regression, Random Forest, and XGBoost classifiers.
    Select the best model based on validation performance.
    
    Returns a dict with training results and metrics.
    """
    from sklearn.model_selection import train_test_split
    from sklearn.linear_model import LogisticRegression
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import (
        accuracy_score, precision_score, recall_score,
        f1_score, confusion_matrix, classification_report,
    )
    import joblib

    if save_dir is None:
        from app.config import settings
        save_dir = settings.TRAINED_MODEL_DIR

    X = np.vstack(features_list)
    y = np.array(labels)

    # Handle case with too few samples
    if len(X) < 10:
        logger.warning(f"Only {len(X)} samples available. Need at least 10 for training.")
        return {"status": "insufficient_data", "sample_count": len(X)}

    # Split data
    test_size = 0.2 if len(X) > 50 else 0.3
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42, stratify=y if len(np.unique(y)) > 1 else None
    )

    # Define models
    models = {
        "logistic_regression": LogisticRegression(
            max_iter=1000, random_state=42, multi_class="multinomial"
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=100, random_state=42, max_depth=10
        ),
    }

    # Try to add XGBoost
    try:
        import xgboost as xgb
        models["xgboost"] = xgb.XGBClassifier(
            n_estimators=100, max_depth=6, random_state=42,
            use_label_encoder=False, eval_metric="mlogloss",
        )
    except ImportError:
        logger.warning("XGBoost not available, skipping.")

    results = {}
    best_model = None
    best_f1 = -1
    best_name = None

    for name, model in models.items():
        try:
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)

            # Compute metrics
            avg_method = "weighted" if len(np.unique(y)) > 2 else "binary"
            metrics = {
                "accuracy": float(accuracy_score(y_test, y_pred)),
                "precision": float(precision_score(y_test, y_pred, average=avg_method, zero_division=0)),
                "recall": float(recall_score(y_test, y_pred, average=avg_method, zero_division=0)),
                "f1_score": float(f1_score(y_test, y_pred, average=avg_method, zero_division=0)),
                "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
            }

            results[name] = metrics
            logger.info(f"{name}: F1={metrics['f1_score']:.4f}, Acc={metrics['accuracy']:.4f}")

            if metrics["f1_score"] > best_f1:
                best_f1 = metrics["f1_score"]
                best_model = model
                best_name = name

        except Exception as e:
            logger.error(f"Training {name} failed: {e}")
            results[name] = {"error": str(e)}

    if best_model is None:
        return {"status": "training_failed", "results": results}

    # Save the best model
    os.makedirs(save_dir, exist_ok=True)
    model_path = os.path.join(save_dir, "trained_model.pkl")
    joblib.dump(best_model, model_path)

    metadata = {
        "best_model": best_name,
        "best_f1": best_f1,
        "feature_names": FEATURE_NAMES,
        "label_map": LABEL_MAP,
        "training_samples": len(X),
        "results": results,
    }
    meta_path = os.path.join(save_dir, "model_metadata.json")
    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=2)

    logger.info(f"Best model: {best_name} (F1={best_f1:.4f}), saved to {model_path}")

    return {"status": "success", "best_model": best_name, **metadata}


def load_model(model_dir: str = None) -> Optional[Any]:
    """Load the trained model from disk."""
    global _trained_model, _model_metadata

    if _trained_model is not None:
        return _trained_model

    if model_dir is None:
        from app.config import settings
        model_dir = settings.TRAINED_MODEL_DIR

    model_path = os.path.join(model_dir, "trained_model.pkl")
    meta_path = os.path.join(model_dir, "model_metadata.json")

    if not os.path.exists(model_path):
        logger.info("No trained model found. Using rule-based classification.")
        return None

    try:
        import joblib
        _trained_model = joblib.load(model_path)

        if os.path.exists(meta_path):
            with open(meta_path, "r") as f:
                _model_metadata = json.load(f)

        logger.info(f"Loaded trained model from {model_path}")
        return _trained_model
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        return None


def predict(features: np.ndarray) -> Tuple[str, float]:
    """
    Predict match classification using the trained model.
    Falls back to rule-based classification if no model is available.
    """
    model = load_model()

    if model is None:
        # Rule-based fallback
        avg_score = float(np.mean(features[0, :6])) * 100
        from app.services.matcher import classify_match
        return classify_match(avg_score)

    try:
        prediction = int(model.predict(features)[0])
        label = LABEL_MAP.get(prediction, "Unknown")

        # Get confidence if available
        if hasattr(model, "predict_proba"):
            proba = model.predict_proba(features)[0]
            confidence = float(max(proba))
        else:
            confidence = 0.7  # Default confidence

        return label, confidence
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        avg_score = float(np.mean(features[0, :6])) * 100
        from app.services.matcher import classify_match
        return classify_match(avg_score)


def explain_prediction(features: np.ndarray) -> List[Dict[str, Any]]:
    """
    Use SHAP to explain the model's prediction.
    Returns a list of feature contributions.
    """
    model = load_model()

    if model is None:
        # Rule-based explanation (no SHAP without a model)
        explanations = []
        feature_values = features[0]
        for i, name in enumerate(FEATURE_NAMES):
            value = float(feature_values[i])
            # Simple rule: positive if above 0.5, negative if below
            contribution = (value - 0.5) * 2
            explanations.append({
                "feature": name,
                "value": round(value, 4),
                "contribution": round(contribution, 4),
            })
        return sorted(explanations, key=lambda x: abs(x["contribution"]), reverse=True)

    try:
        import shap

        # Use appropriate explainer based on model type
        model_type = type(model).__name__
        
        if model_type in ("XGBClassifier",):
            explainer = shap.TreeExplainer(model)
        elif model_type in ("RandomForestClassifier",):
            explainer = shap.TreeExplainer(model)
        else:
            # Use KernelExplainer for models without tree structure
            explainer = shap.KernelExplainer(
                model.predict_proba if hasattr(model, "predict_proba") else model.predict,
                shap.sample(features, min(100, len(features))),
            )

        shap_values = explainer.shap_values(features)

        # Handle multi-class SHAP values
        if isinstance(shap_values, list):
            # Use the SHAP values for the predicted class
            prediction = int(model.predict(features)[0])
            shap_vals = shap_values[prediction][0] if prediction < len(shap_values) else shap_values[0][0]
        else:
            shap_vals = shap_values[0]

        explanations = []
        for i, name in enumerate(FEATURE_NAMES):
            explanations.append({
                "feature": name,
                "value": round(float(features[0, i]), 4),
                "contribution": round(float(shap_vals[i]), 4),
            })

        return sorted(explanations, key=lambda x: abs(x["contribution"]), reverse=True)

    except Exception as e:
        logger.error(f"SHAP explanation failed: {e}")
        # Fallback to rule-based
        explanations = []
        feature_values = features[0]
        for i, name in enumerate(FEATURE_NAMES):
            value = float(feature_values[i])
            contribution = (value - 0.5) * 2
            explanations.append({
                "feature": name,
                "value": round(value, 4),
                "contribution": round(contribution, 4),
            })
        return sorted(explanations, key=lambda x: abs(x["contribution"]), reverse=True)
