"""
main.py ? CricSim-X Unified Orchestration CLI
Live-Contextual Match Simulator & Strategic Franchise Optimizer for IPL 2026

Usage:
    python main.py --mode setup    # Initialize DB and generate data
    python main.py --mode train    # Train all models
    python main.py --mode predict  # Run simulations on 2026 schedule
    python main.py --mode all      # Full sequential pipeline
"""

import argparse
import os
import sys
import json
import numpy as np
import pandas as pd

# --- Project imports -------------------------------------------------------
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config

from src.data_pipeline      import run_pipeline, query_venue_stats
from src.feature_engineering import build_feature_matrix, compute_ema_form
from src.model_factory       import train_and_evaluate, save_models
from src.simulator           import simulate_win_probability_simple, predict_schedule


# -------------------------------------------------------------
# Banner
# -------------------------------------------------------------
BANNER = """
==========================================================
   CricSim-X  |  IPL 2026 Match Intelligence Platform
   Live-Contextual Match Simulator & Franchise Optimizer
   18 Seasons of Ball-by-Ball Data (2008-2025)
=========================================================="""


# -------------------------------------------------------------
# Pipeline Stages
# -------------------------------------------------------------
def stage_setup() -> pd.DataFrame:
    """Initialize project environment: generate data and build SQLite DB."""
    print("\n[SETUP] -- Initializing CricSim-X Environment ------------------")
    print("\n[SETUP] -- Initializing CricSim-X Environment ------------------")
    os.makedirs(config.MODELS_DIR, exist_ok=True)
    os.makedirs(config.RESULTS_DIR, exist_ok=True)

    df = run_pipeline()

    print(f"\n[SETUP] Done. {len(df)} match records loaded into SQLite cache.")
    print(f"        DB Path  -> {config.DB_PATH}")
    print(f"        Raw CSV  -> {config.RAW_IPL_CSV}")
    print(f"        Schedule -> {config.SCHEDULE_CSV}")
    return df


def stage_train(df: pd.DataFrame) -> dict:
    """Extract features and train the stacking meta-classifier."""
    print("\n[TRAIN] -- Feature Engineering ---------------------------------")

    # Build venue stats from SQLite
    from src.data_pipeline import query_venue_stats
    venue_stats = {}
    for venue in config.VENUES:
        venue_stats[venue] = query_venue_stats(venue, config.DB_PATH)

    X, y, scaler = build_feature_matrix(df, venue_stats)
    np.save(config.PROCESSED_X, X)
    np.save(config.PROCESSED_Y, y)
    print(f"[TRAIN] Feature matrix saved: X={X.shape}, y={y.shape}")
    # Note: ensure output dir exists
    import os; os.makedirs(config.RESULTS_DIR, exist_ok=True)

    print("\n[TRAIN] -- Model Training ---------------------------------------")
    metrics, trained_models, X_test, y_test = train_and_evaluate(X, y)
    save_models(trained_models, metrics, scaler)

    print("\n[TRAIN] -- Performance Summary ----------------------------------")
    print(f"  {'Model':<24} {'CV Acc':>8} {'Test Acc':>10} {'AUC':>8}")
    print("  " + "-" * 54)
    for name, m in metrics.items():
        cv  = f"{m['cv_acc']:.4f}" if m['cv_acc'] else "   N/A"
        print(f"  {name:<24} {cv:>8} {m['test_acc']:>10.4f} {m['auc']:>8.4f}")

    return metrics


def stage_predict() -> pd.DataFrame:
    """Run win-probability simulations for all IPL 2026 fixtures."""
    print("\n[PREDICT] -- IPL 2026 Schedule Simulation -----------------------")

    if not os.path.exists(config.SCHEDULE_CSV):
        print("[PREDICT] Schedule not found ? running setup first...")
        stage_setup()

    schedule_df = pd.read_csv(config.SCHEDULE_CSV)
    raw_df = pd.read_csv(config.RAW_IPL_CSV)
    raw_df["date"] = pd.to_datetime(raw_df["date"], errors="coerce")

    # Get latest EMA state
    _, ema_state = compute_ema_form(raw_df)

    # Build venue stats
    from src.data_pipeline import query_venue_stats
    venue_stats = {}
    for venue in config.VENUES:
        venue_stats[venue] = query_venue_stats(venue, config.DB_PATH)

    results_df = predict_schedule(schedule_df, ema_state, venue_stats)

    out_path = os.path.join(config.RESULTS_DIR, "ipl2026_predictions.csv")
    results_df.to_csv(out_path, index=False)

    # Also save as JSON for dashboard consumption
    json_path = os.path.join(config.RESULTS_DIR, "ipl2026_predictions.json")
    results_df.to_json(json_path, orient="records", indent=2)

    print(f"\n[PREDICT] Predictions saved -> {out_path}")
    print(f"\n  Sample Results (first 5 fixtures):")
    print(f"  {'#':>3}  {'Team 1':<30} {'Team 2':<30} {'Pred Winner':<30} {'Conf':>6}")
    print("  " + "-" * 105)
    for _, row in results_df.head(5).iterrows():
        conf = max(row["win_prob_t1"], row["win_prob_t2"])
        print(f"  {row['match_id']:>3}  {row['team1']:<30} {row['team2']:<30} "
              f"{row['predicted_winner']:<30} {conf:>5.1f}%")

    return results_df


# -------------------------------------------------------------
# Main Entry Point
# -------------------------------------------------------------
def main():
    print(BANNER)

    parser = argparse.ArgumentParser(
        description="CricSim-X: Live-Contextual IPL Match Simulator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--mode",
        choices=["setup", "train", "predict", "all"],
        required=True,
        help=(
            "setup   -> Initialize DB and generate synthetic data\n"
            "train   -> Extract features and train ML models\n"
            "predict -> Simulate IPL 2026 schedule outcomes\n"
            "all     -> Run complete pipeline sequentially"
        ),
    )
    args = parser.parse_args()

    if args.mode == "setup":
        stage_setup()

    elif args.mode == "train":
        if not os.path.exists(config.RAW_IPL_CSV):
            print("[TRAIN] Raw data not found ? running setup first...")
            df = stage_setup()
        else:
            df = pd.read_csv(config.RAW_IPL_CSV)
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
        stage_train(df)

    elif args.mode == "predict":
        stage_predict()

    elif args.mode == "all":
        df = stage_setup()
        stage_train(df)
        stage_predict()
        print("\n[ALL] -- CricSim-X Pipeline Complete ------------------------")
        print("  Open dashboard/index.html in your browser to explore results.")

    print("\n")


if __name__ == "__main__":
    main()
