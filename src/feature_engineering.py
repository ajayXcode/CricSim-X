"""
feature_engineering.py ? EMA Team Form, RRR, Wicket Pressure & Venue Leverage
CricSim-X | src/feature_engineering.py
"""

import os
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


# -------------------------------------------------------------
# A. Team Form Index via Exponential Moving Average
# -------------------------------------------------------------
def compute_ema_form(df: pd.DataFrame, alpha: float = config.EMA_ALPHA) -> pd.DataFrame:
    """
    Compute EMA-based team form index for each team across seasons.

    Formula (from documentation):
        EMA_t = (NRR_t ? alpha) + (EMA_{t-1} ? (1 - alpha))

    Where alpha = 0.35 balances recent form vs. foundational capability.
    """
    df = df.sort_values("date").reset_index(drop=True)
    ema_state: dict[str, float] = {team: 0.0 for team in config.TEAMS}

    ema_team1 = []
    ema_team2 = []

    for _, row in df.iterrows():
        t1, t2 = row["team1"], row["team2"]
        nrr1 = row.get("nrr_team1", 0.0) or 0.0
        nrr2 = row.get("nrr_team2", 0.0) or 0.0

        # Capture EMA before update (pre-match state)
        ema_team1.append(ema_state.get(t1, 0.0))
        ema_team2.append(ema_state.get(t2, 0.0))

        # Update EMA post-match
        ema_state[t1] = (nrr1 * alpha) + (ema_state.get(t1, 0.0) * (1 - alpha))
        ema_state[t2] = (nrr2 * alpha) + (ema_state.get(t2, 0.0) * (1 - alpha))

    df["ema_team1"] = ema_team1
    df["ema_team2"] = ema_team2

    print(f"[FeatureEng] EMA form computed for {len(config.TEAMS)} franchises (alpha={alpha}).")
    return df, ema_state


# -------------------------------------------------------------
# B. Required Run Rate (RRR) ? Ball-by-Ball
# -------------------------------------------------------------
def compute_rrr(runs_required: int, balls_remaining: int) -> float:
    """
    RRR = (Runs Required) / (Balls Remaining / 6)

    Returns float 0.0 if balls_remaining == 0 (match over).
    """
    if balls_remaining <= 0:
        return 0.0
    return round(runs_required / (balls_remaining / 6), 2)


# -------------------------------------------------------------
# C. Wicket Pressure Index
# -------------------------------------------------------------
def compute_wicket_pressure(wickets_lost: int, decay_base: float = config.WICKET_DECAY_BASE) -> float:
    """
    Exponential decay factor reflecting batting resource depletion.

    WPI = decay_base ^ wickets_lost
    A team at 0 wickets has WPI=1.0; at 10 wickets WPI->0.
    """
    wickets_lost = max(0, min(10, wickets_lost))
    wpi = decay_base ** wickets_lost
    return round(wpi, 4)


# -------------------------------------------------------------
# D. Venue Leverage Factor
# -------------------------------------------------------------
def compute_venue_leverage(venue: str, is_day_night: bool,
                            venue_stats: dict) -> float:
    """
    Historical win percentage adjusted for D/N conditions.

    venue_leverage = base_win_pct + (day_night_boost if D/N)
    """
    stats = venue_stats.get(venue, {})
    total = stats.get("total_matches", 1)
    batting_wins = stats.get("batting_first_wins", total // 2)
    base_pct = batting_wins / max(total, 1)

    dn_boost = config.VENUE_LIGHTS_BOOST if is_day_night else 0.0
    leverage = round(base_pct + dn_boost, 4)
    return leverage


# -------------------------------------------------------------
# E. Full Feature Matrix Builder
# -------------------------------------------------------------
def build_feature_matrix(df: pd.DataFrame, venue_stats: dict) -> tuple[np.ndarray, np.ndarray]:
    """
    Construct the multi-dimensional feature matrix X and label vector y.

    Features per match (normalised):
        [ema_team1, ema_team2, ema_diff,
         innings1_score, innings2_score, target,
         wicket_pressure_inn2, venue_leverage,
         toss_advantage, rrr_mid_innings]

    Label:
        1 = team2 (chasing) won, 0 = team1 (batting first) won
    """
    df, _ = compute_ema_form(df)

    feature_rows = []
    labels = []

    for _, row in df.iterrows():
        venue = row["venue"]
        dn    = bool(row.get("day_night", False))

        ema1 = row["ema_team1"]
        ema2 = row["ema_team2"]
        ema_diff = ema1 - ema2

        target_runs = row["innings1_score"] + 1
        runs_scored  = row["innings2_score"]
        wickets_inn2 = row["innings2_wickets"]

        # Mid-innings proxy: assume halfway point
        halfway_balls = 60
        rrr = compute_rrr(target_runs - runs_scored // 2, halfway_balls)
        wpi = compute_wicket_pressure(wickets_inn2 // 2)
        vl  = compute_venue_leverage(venue, dn, venue_stats)

        # Toss advantage: 1 if chasing team won toss
        toss_adv = 1 if row["toss_winner"] == row["innings2_team"] else 0

        feature_rows.append([
            ema1, ema2, ema_diff,
            row["innings1_score"], row["innings2_score"], target_runs,
            wpi, vl, toss_adv, rrr,
        ])

        labels.append(1 if row["winner"] == row["innings2_team"] else 0)

    X = np.array(feature_rows, dtype=np.float32)
    y = np.array(labels, dtype=np.int32)

    # Normalise to [0, 1]
    from sklearn.preprocessing import MinMaxScaler
    scaler = MinMaxScaler()
    X = scaler.fit_transform(X)

    print(f"[FeatureEng] Feature matrix: {X.shape}, Label distribution: {dict(zip(*np.unique(y, return_counts=True)))}")
    return X, y, scaler


# -------------------------------------------------------------
# Live Inference Feature Vector
# -------------------------------------------------------------
def build_live_feature_vector(
    current_score: int,
    wickets_lost: int,
    balls_left: int,
    target: int,
    ema_chasing: float,
    ema_batting: float,
    venue_leverage: float,
    toss_advantage: int,
    scaler=None,
) -> np.ndarray:
    """
    Construct a single feature vector for live match-state inference.
    Mirrors the columns used during training.
    """
    rrr = compute_rrr(target - current_score, balls_left)
    wpi = compute_wicket_pressure(wickets_lost)
    ema_diff = ema_batting - ema_chasing

    vec = np.array([[
        ema_batting, ema_chasing, ema_diff,
        target - 1, current_score, target,
        wpi, venue_leverage, toss_advantage, rrr,
    ]], dtype=np.float32)

    if scaler is not None:
        vec = scaler.transform(vec)

    return vec


if __name__ == "__main__":
    # Quick sanity check
    print("RRR (need 80 off 60 balls):", compute_rrr(80, 60))
    print("Wicket Pressure (5 down):", compute_wicket_pressure(5))
    print("Venue Leverage (Wankhede, D/N, no stats):", compute_venue_leverage("Wankhede", True, {}))
