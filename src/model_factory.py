"""
model_factory.py ? Stacking Meta-Classifier (XGBoost + LightGBM + RF + MLP + ExtraTrees)
CricSim-X | src/model_factory.py
"""

import os
import sys
import json
import time
import joblib
import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier, StackingClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.preprocessing import MinMaxScaler

try:
    import xgboost as xgb
    HAS_XGB = True
except ImportError:
    HAS_XGB = False
    print("[ModelFactory] WARNING: xgboost not installed ? using GradientBoosting fallback.")
    from sklearn.ensemble import GradientBoostingClassifier

try:
    import lightgbm as lgb
    HAS_LGB = True
except ImportError:
    HAS_LGB = False
    print("[ModelFactory] WARNING: lightgbm not installed ? using GradientBoosting fallback.")
    from sklearn.ensemble import GradientBoostingClassifier

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


# -------------------------------------------------------------
# Base Learner Builders
# -------------------------------------------------------------
def build_random_forest() -> RandomForestClassifier:
    return RandomForestClassifier(**config.RF_PARAMS)


def build_xgboost():
    if HAS_XGB:
        params = {k: v for k, v in config.XGB_PARAMS.items() if k != "use_label_encoder"}
        return xgb.XGBClassifier(**params, use_label_encoder=False)
    return GradientBoostingClassifier(n_estimators=300, max_depth=6, learning_rate=0.05, random_state=42)


def build_lightgbm():
    if HAS_LGB:
        return lgb.LGBMClassifier(**config.LGBM_PARAMS)
    return GradientBoostingClassifier(n_estimators=300, max_depth=6, learning_rate=0.05, random_state=43)


def build_mlp() -> MLPClassifier:
    return MLPClassifier(**config.MLP_PARAMS)


def build_extra_trees() -> ExtraTreesClassifier:
    return ExtraTreesClassifier(**config.ET_PARAMS)


# -------------------------------------------------------------
# Stacking Meta-Classifier
# -------------------------------------------------------------
def build_stacking_ensemble() -> StackingClassifier:
    """
    Assembles the CricSim-X Meta-Ensemble:
    Base learners -> LogisticRegression meta-learner.
    """
    estimators = [
        ("rf",   build_random_forest()),
        ("xgb",  build_xgboost()),
        ("lgbm", build_lightgbm()),
        ("mlp",  build_mlp()),
        ("et",   build_extra_trees()),
    ]
    meta_learner = LogisticRegression(**config.META_PARAMS)

    stacking = StackingClassifier(
        estimators=estimators,
        final_estimator=meta_learner,
        cv=5,
        stack_method="predict_proba",
        n_jobs=-1,
        verbose=0,
    )
    return stacking


# -------------------------------------------------------------
# Training & Evaluation
# -------------------------------------------------------------
def train_and_evaluate(X: np.ndarray, y: np.ndarray) -> dict:
    """
    Train all individual models + stacking ensemble.
    Returns performance metrics matching documented figures.
    """
    from sklearn.model_selection import train_test_split

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )

    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    models = {
        "Random Forest":  build_random_forest(),
        "XGBoost":        build_xgboost(),
        "LightGBM":       build_lightgbm(),
        "Neural Network": build_mlp(),
        "ExtraTrees":     build_extra_trees(),
    }

    metrics = {}
    trained_models = {}

    print("\n[ModelFactory] -- Training Individual Base Learners --")
    for name, model in models.items():
        t0 = time.time()

        # Cross-validation accuracy
        cv_scores = cross_val_score(model, X_train, y_train, cv=skf, scoring="accuracy", n_jobs=-1)
        cv_acc = float(cv_scores.mean())

        # Fit and evaluate on test set
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1]

        test_acc = float(accuracy_score(y_test, y_pred))
        test_auc = float(roc_auc_score(y_test, y_proba))

        elapsed = time.time() - t0
        metrics[name] = {
            "cv_acc":   round(cv_acc, 4),
            "test_acc": round(test_acc, 4),
            "auc":      round(test_auc, 4),
            "train_sec": round(elapsed, 1),
        }
        trained_models[name] = model
        print(f"  {name:22s} | CV={cv_acc:.4f} | TestAcc={test_acc:.4f} | AUC={test_auc:.4f} | {elapsed:.1f}s")

    # -- Stacking Ensemble --
    print("\n[ModelFactory] -- Training CricSim-X Stacking Ensemble --")
    t0 = time.time()
    ensemble = build_stacking_ensemble()
    ensemble.fit(X_train, y_train)

    y_pred_ens  = ensemble.predict(X_test)
    y_proba_ens = ensemble.predict_proba(X_test)[:, 1]
    ens_acc  = float(accuracy_score(y_test, y_pred_ens))
    ens_auc  = float(roc_auc_score(y_test, y_proba_ens))
    elapsed  = time.time() - t0

    metrics["CricSim-X Ensemble"] = {
        "cv_acc":   None,
        "test_acc": round(ens_acc, 4),
        "auc":      round(ens_auc, 4),
        "train_sec": round(elapsed, 1),
    }
    trained_models["CricSim-X Ensemble"] = ensemble
    print(f"  {'CricSim-X Ensemble':22s} | TestAcc={ens_acc:.4f} | AUC={ens_auc:.4f} | {elapsed:.1f}s")

    return metrics, trained_models, X_test, y_test


# -------------------------------------------------------------
# Model Persistence
# -------------------------------------------------------------
def save_models(trained_models: dict, metrics: dict, scaler) -> None:
    """Serialize all trained models and metrics to disk."""
    os.makedirs(config.MODELS_DIR, exist_ok=True)

    for name, model in trained_models.items():
        fname = name.replace(" ", "_").replace("-", "_").lower() + ".pkl"
        fpath = os.path.join(config.MODELS_DIR, fname)
        joblib.dump(model, fpath)
        print(f"[ModelFactory] Saved -> {fpath}")

    # Save scaler
    joblib.dump(scaler, os.path.join(config.MODELS_DIR, "scaler.pkl"))

    # Save metrics as JSON for dashboard consumption
    metrics_path = os.path.join(config.RESULTS_DIR, "model_metrics.json")
    os.makedirs(config.RESULTS_DIR, exist_ok=True)
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[ModelFactory] Metrics saved -> {metrics_path}")


def load_ensemble(model_name: str = "cricsim_x_ensemble"):
    """Load the serialized ensemble model and scaler."""
    fname = model_name + ".pkl"
    fpath = os.path.join(config.MODELS_DIR, fname)
    if not os.path.exists(fpath):
        raise FileNotFoundError(f"Model not found at {fpath}. Run --mode train first.")
    model = joblib.load(fpath)
    scaler = joblib.load(os.path.join(config.MODELS_DIR, "scaler.pkl"))
    return model, scaler


if __name__ == "__main__":
    print("[ModelFactory] Standalone test ? generating dummy data...")
    rng = np.random.default_rng(0)
    X = rng.random((500, 10)).astype(np.float32)
    y = rng.integers(0, 2, size=500)
    metrics, models, _, _ = train_and_evaluate(X, y)
    print("\nFinal Metrics:")
    for k, v in metrics.items():
        print(f"  {k}: {v}")
