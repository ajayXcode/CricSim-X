"""
simulator.py ? Dynamic Monte Carlo Markov Chain Match Simulator
CricSim-X | src/simulator.py
"""

import os
import sys
import json
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


# -------------------------------------------------------------
# Core Monte Carlo Simulation (as documented)
# -------------------------------------------------------------
def simulate_match_chase(
    target: int,
    current_score: int,
    wickets_lost: int,
    balls_left: int,
    model,
    venue_features: list,
    n_simulations: int = config.N_SIMULATIONS,
    rng_seed: int = None,
) -> float:
    """
    Stochastic Monte Carlo simulator ? exactly as documented in CricSim-X spec.

    Forks any live game instance into N=10,000 parallel Markov Chain paths.

    Args:
        target:         Runs required by chasing team
        current_score:  Runs on the board at simulation time
        wickets_lost:   Wickets fallen so far
        balls_left:     Balls remaining in the innings
        model:          Trained sklearn-compatible classifier
        venue_features: Venue/context features list (appended to state vector)
        n_simulations:  Number of parallel simulation paths (default 10,000)

    Returns:
        Win probability percentage (0?100)
    """
    rng = np.random.default_rng(rng_seed)

    win_count = 0
    simulations = n_simulations

    for _ in range(simulations):
        temp_score   = current_score
        temp_wickets = wickets_lost
        temp_balls   = balls_left

        while temp_balls > 0 and temp_wickets < 10 and temp_score <= target:
            # Vector structure mapping to current state
            features = np.array([[temp_score, temp_wickets, temp_balls,
                                   *venue_features]])

            prob_win = model.predict_proba(features)[0][1]

            # Stochastic state adjustment
            if rng.random() < prob_win:
                temp_score += rng.choice(
                    config.SCORING_RUNS,
                    p=config.SCORING_PROBS
                )
            else:
                temp_wickets += 1

            temp_balls -= 1

        if temp_score > target:
            win_count += 1

    return round((win_count / simulations) * 100, 2)


# -------------------------------------------------------------
# Simplified Model-Free Simulator (for dashboard / demo)
# -------------------------------------------------------------
def simulate_win_probability_simple(
    target: int,
    current_score: int,
    wickets_lost: int,
    balls_left: int,
    ema_chasing: float = 0.0,
    ema_batting: float = 0.0,
    venue_leverage: float = 0.5,
    n_simulations: int = config.N_SIMULATIONS,
    rng_seed: int = 42,
) -> float:
    """
    Model-free Monte Carlo simulator using heuristic win probability.
    Used for dashboard demos when no trained model is loaded.

    The base probability is derived from:
        - RRR vs scoring rate distribution
        - Wicket pressure index
        - EMA form differential
        - Venue leverage
    """
    from src.feature_engineering import compute_rrr, compute_wicket_pressure

    rng = np.random.default_rng(rng_seed)

    runs_needed = target - current_score
    if runs_needed <= 0:
        return 100.0
    if balls_left <= 0 or wickets_lost >= 10:
        return 0.0

    rrr = compute_rrr(runs_needed, balls_left)
    wpi = compute_wicket_pressure(wickets_lost)

    # Heuristic base probability (calibrated to match historical AUC ~0.71)
    avg_run_rate  = 8.0 + ema_chasing * 2.0           # expected scoring rate
    rate_ratio    = avg_run_rate / max(rrr, 0.1)       # scoring vs required
    base_prob     = rate_ratio / (1 + rate_ratio)      # logistic squash

    # Adjust for wicket pressure and venue
    adjusted_prob = base_prob * wpi * (0.85 + venue_leverage * 0.3)
    adjusted_prob = float(np.clip(adjusted_prob, 0.05, 0.95))

    # Monte Carlo
    win_count = 0
    for _ in range(n_simulations):
        temp_score   = current_score
        temp_wickets = wickets_lost
        temp_balls   = balls_left

        while temp_balls > 0 and temp_wickets < 10 and temp_score <= target:
            if rng.random() < adjusted_prob:
                temp_score += int(rng.choice(config.SCORING_RUNS, p=config.SCORING_PROBS))
            else:
                temp_wickets += 1
            temp_balls -= 1

        if temp_score > target:
            win_count += 1

    return round((win_count / n_simulations) * 100, 2)


# -------------------------------------------------------------
# Path Recorder (for visualisation)
# -------------------------------------------------------------
def simulate_paths(
    target: int,
    current_score: int,
    wickets_lost: int,
    balls_left: int,
    ema_chasing: float = 0.0,
    venue_leverage: float = 0.5,
    n_paths: int = 100,
    rng_seed: int = 42,
) -> list[dict]:
    """
    Run a reduced number of paths and record ball-by-ball score trajectories.
    Used for the Monte Carlo visualisation panel in the dashboard.

    Returns:
        List of {path_id, balls, scores, won} dicts
    """
    from src.feature_engineering import compute_rrr, compute_wicket_pressure

    rng = np.random.default_rng(rng_seed)

    runs_needed   = target - current_score
    rrr           = compute_rrr(runs_needed, balls_left)
    wpi           = compute_wicket_pressure(wickets_lost)
    avg_run_rate  = 8.0 + ema_chasing * 2.0
    rate_ratio    = avg_run_rate / max(rrr, 0.1)
    base_prob     = rate_ratio / (1 + rate_ratio)
    adjusted_prob = float(np.clip(base_prob * wpi * (0.85 + venue_leverage * 0.3), 0.05, 0.95))

    paths = []
    for path_id in range(n_paths):
        temp_score   = current_score
        temp_wickets = wickets_lost
        temp_balls   = balls_left
        score_traj   = [temp_score]
        ball_traj    = [120 - balls_left]

        while temp_balls > 0 and temp_wickets < 10 and temp_score <= target:
            if rng.random() < adjusted_prob:
                temp_score += int(rng.choice(config.SCORING_RUNS, p=config.SCORING_PROBS))
            else:
                temp_wickets += 1
            temp_balls -= 1
            score_traj.append(temp_score)
            ball_traj.append(120 - temp_balls)

        paths.append({
            "path_id": path_id,
            "balls":   ball_traj,
            "scores":  score_traj,
            "won":     temp_score > target,
        })

    return paths


# -------------------------------------------------------------
# Batch Prediction for Schedule
# -------------------------------------------------------------
def predict_schedule(schedule_df: pd.DataFrame, ema_state: dict,
                     venue_stats: dict) -> pd.DataFrame:
    """
    Run win probability simulation for each fixture in the IPL 2026 schedule.
    Uses simplified heuristic model (no trained ML model needed post-setup).
    """
    results = []
    for _, row in schedule_df.iterrows():
        t1 = row["team1"]
        t2 = row["team2"]
        venue = row["venue"]

        ema1 = ema_state.get(t1, 0.0)
        ema2 = ema_state.get(t2, 0.0)

        # Average match state (mid-game estimate)
        vl = venue_stats.get(venue, {}).get("batting_first_wins", 30)
        vl = vl / max(venue_stats.get(venue, {}).get("total_matches", 60), 1)

        win_prob_t1 = simulate_win_probability_simple(
            target=165, current_score=82, wickets_lost=3, balls_left=60,
            ema_chasing=ema2, ema_batting=ema1,
            venue_leverage=vl, n_simulations=1000,
        )
        win_prob_t2 = round(100 - win_prob_t1, 2)

        results.append({
            "match_id":      row["match_id"],
            "date_utc":      row["date_utc"],
            "team1":         t1,
            "team2":         t2,
            "venue":         venue,
            "win_prob_t1":   win_prob_t1,
            "win_prob_t2":   win_prob_t2,
            "predicted_winner": t1 if win_prob_t1 >= 50 else t2,
        })

    return pd.DataFrame(results)


if __name__ == "__main__":
    # Quick standalone test
    prob = simulate_win_probability_simple(
        target=180, current_score=95, wickets_lost=3, balls_left=54,
        ema_chasing=0.12, ema_batting=-0.05, venue_leverage=0.55, n_simulations=5000,
    )
    print(f"[Simulator] Win probability: {prob:.1f}%")
