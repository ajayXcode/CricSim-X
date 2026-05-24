"""
config.py ? CricSim-X Global Configuration
Live-Contextual Match Simulator & Strategic Franchise Optimizer for IPL 2026
"""

import os

# -------------------------------------------------------------
# Project Root Paths
# -------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR       = os.path.join(BASE_DIR, "data")
RAW_DIR        = os.path.join(DATA_DIR, "raw")
PROCESSED_DIR  = os.path.join(DATA_DIR, "processed")
DB_DIR         = os.path.join(DATA_DIR, "db")

OUTPUT_DIR     = os.path.join(BASE_DIR, "outputs")
MODELS_DIR     = os.path.join(OUTPUT_DIR, "models")
RESULTS_DIR    = os.path.join(OUTPUT_DIR, "results")

DB_PATH        = os.path.join(DB_DIR, "cricsim_cache.db")
RAW_IPL_CSV    = os.path.join(RAW_DIR, "IPL.csv")
SCHEDULE_CSV   = os.path.join(RAW_DIR, "ipl-2026-UTC.csv")

PROCESSED_X    = os.path.join(PROCESSED_DIR, "X_features.npy")
PROCESSED_Y    = os.path.join(PROCESSED_DIR, "y_labels.npy")

# -------------------------------------------------------------
# Feature Engineering Parameters
# -------------------------------------------------------------
EMA_ALPHA          = 0.35       # Exponential Moving Average smoothing factor
VENUE_LIGHTS_BOOST = 0.08       # Venue leverage under D/N conditions
WICKET_DECAY_BASE  = 0.92       # Exponential decay base for Wicket Pressure Index

# -------------------------------------------------------------
# Monte Carlo Simulation Settings
# -------------------------------------------------------------
N_SIMULATIONS = 10_000          # Parallel stochastic paths per match state
SCORING_PROBS  = [0.4, 0.1, 0.3, 0.2]   # Run scoring distribution: [1, 2, 4, 6]
SCORING_RUNS   = [1, 2, 4, 6]

# -------------------------------------------------------------
# IPL Franchise Registry (2026)
# -------------------------------------------------------------
TEAMS = [
    "Mumbai Indians",
    "Chennai Super Kings",
    "Royal Challengers Bengaluru",
    "Kolkata Knight Riders",
    "Rajasthan Royals",
    "Delhi Capitals",
    "Punjab Kings",
    "Sunrisers Hyderabad",
    "Gujarat Titans",
    "Lucknow Super Giants",
]

TEAM_SHORT = {
    "Mumbai Indians":               "MI",
    "Chennai Super Kings":          "CSK",
    "Royal Challengers Bengaluru":  "RCB",
    "Kolkata Knight Riders":        "KKR",
    "Rajasthan Royals":             "RR",
    "Delhi Capitals":               "DC",
    "Punjab Kings":                 "PBKS",
    "Sunrisers Hyderabad":          "SRH",
    "Gujarat Titans":               "GT",
    "Lucknow Super Giants":         "LSG",
}

# -------------------------------------------------------------
# IPL Venues (2026 Season)
# -------------------------------------------------------------
VENUES = [
    "Wankhede Stadium, Mumbai",
    "M.A. Chidambaram Stadium, Chennai",
    "M. Chinnaswamy Stadium, Bengaluru",
    "Eden Gardens, Kolkata",
    "Sawai Mansingh Stadium, Jaipur",
    "Arun Jaitley Stadium, Delhi",
    "Punjab Cricket Association Stadium, Mohali",
    "Rajiv Gandhi International Stadium, Hyderabad",
    "Narendra Modi Stadium, Ahmedabad",
    "Ekana Cricket Stadium, Lucknow",
]

# -------------------------------------------------------------
# Model Hyperparameters
# -------------------------------------------------------------
RF_PARAMS = {
    "n_estimators": 200,
    "max_depth": 8,
    "min_samples_split": 5,
    "random_state": 42,
    "n_jobs": -1,
}

XGB_PARAMS = {
    "n_estimators": 300,
    "max_depth": 6,
    "learning_rate": 0.05,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "use_label_encoder": False,
    "eval_metric": "logloss",
    "random_state": 42,
}

LGBM_PARAMS = {
    "n_estimators": 300,
    "max_depth": 6,
    "learning_rate": 0.05,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "random_state": 42,
    "verbose": -1,
}

MLP_PARAMS = {
    "hidden_layer_sizes": (128, 64, 32),
    "activation": "relu",
    "max_iter": 500,
    "random_state": 42,
    "early_stopping": True,
    "validation_fraction": 0.1,
}

ET_PARAMS = {
    "n_estimators": 200,
    "max_depth": 8,
    "random_state": 42,
    "n_jobs": -1,
}

META_PARAMS = {
    "C": 1.0,
    "max_iter": 1000,
    "random_state": 42,
}

# -------------------------------------------------------------
# Documented Performance Metrics (from research paper)
# -------------------------------------------------------------
BASELINE_METRICS = {
    "Random Forest":      {"cv_acc": 0.6350, "test_acc": 0.6711, "auc": 0.6995},
    "XGBoost":            {"cv_acc": 0.6311, "test_acc": 0.6534, "auc": 0.7111},
    "LightGBM":           {"cv_acc": 0.6477, "test_acc": 0.6600, "auc": 0.7138},
    "Neural Network":     {"cv_acc": 0.6080, "test_acc": 0.6049, "auc": 0.6141},
    "ExtraTrees":         {"cv_acc": 0.6444, "test_acc": 0.6512, "auc": 0.7083},
    "CricSim-X Ensemble": {"cv_acc": None,   "test_acc": 0.6490, "auc": 0.7054},
}
