"""
data_pipeline.py ? ETL, Cleaning & SQLite Cache Builder
CricSim-X | src/data_pipeline.py
"""

import os
import sqlite3
import numpy as np
import pandas as pd
from tqdm import tqdm

# Add parent dir to path so config is importable from src/
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


# -------------------------------------------------------------
# Synthetic Data Generator
# -------------------------------------------------------------
def generate_synthetic_ipl_data(n_matches: int = 1200) -> pd.DataFrame:
    """
    Generate synthetic ball-by-ball IPL data for 18 seasons (2008?2025).
    Each row represents a completed innings/match summary record.
    """
    rng = np.random.default_rng(42)
    teams = config.TEAMS
    venues = config.VENUES

    records = []
    match_id = 1

    for season in range(2008, 2026):
        n_season_matches = n_matches // 18 + (1 if (match_id % 18) < (n_matches % 18) else 0)

        for _ in range(n_season_matches):
            team1, team2 = rng.choice(teams, size=2, replace=False)
            venue = rng.choice(venues)
            toss_winner = rng.choice([team1, team2])
            toss_decision = rng.choice(["bat", "field"])

            # First innings score
            innings1_score = int(rng.integers(120, 230))
            innings1_wickets = int(rng.integers(2, 10))
            innings1_overs = float(rng.uniform(18.0, 20.0))

            # Second innings chase
            innings2_score = int(rng.integers(80, 230))
            innings2_wickets = int(rng.integers(1, 10))
            innings2_overs = float(rng.uniform(10.0, 20.0))

            winner = team1 if innings2_score > innings1_score else team2
            margin = abs(innings2_score - innings1_score)
            margin_type = "runs" if winner == team1 else "wickets"
            margin_val = margin if margin_type == "runs" else int(10 - innings2_wickets)

            is_day_night = rng.random() > 0.3
            nrr1 = round((innings1_score / innings1_overs) - (innings2_score / innings2_overs), 3)
            nrr2 = -nrr1

            records.append({
                "match_id":         match_id,
                "season":           season,
                "date":             f"{season}-{rng.integers(3,5):02d}-{rng.integers(1,30):02d}",
                "venue":            venue,
                "team1":            team1,
                "team2":            team2,
                "toss_winner":      toss_winner,
                "toss_decision":    toss_decision,
                "innings1_team":    team1,
                "innings1_score":   innings1_score,
                "innings1_wickets": innings1_wickets,
                "innings1_overs":   round(innings1_overs, 1),
                "innings2_team":    team2,
                "innings2_score":   innings2_score,
                "innings2_wickets": innings2_wickets,
                "innings2_overs":   round(innings2_overs, 1),
                "winner":           winner,
                "margin":           margin_val,
                "margin_type":      margin_type,
                "day_night":        is_day_night,
                "nrr_team1":        nrr1,
                "nrr_team2":        nrr2,
            })
            match_id += 1

    df = pd.DataFrame(records)
    print(f"[DataPipeline] Generated {len(df)} synthetic match records (2008?2025).")
    return df


def generate_ipl2026_schedule() -> pd.DataFrame:
    """Generate IPL 2026 fixture schedule."""
    rng = np.random.default_rng(99)
    teams = config.TEAMS
    venues = config.VENUES
    fixtures = []

    match_id = 5000
    for week in range(1, 8):
        for _ in range(7):
            team1, team2 = rng.choice(teams, size=2, replace=False)
            venue = rng.choice(venues)
            fixtures.append({
                "match_id":  match_id,
                "date_utc":  f"2026-{3 + week // 4:02d}-{(week * 7 + _) % 28 + 1:02d}T14:00:00Z",
                "team1":     team1,
                "team2":     team2,
                "venue":     venue,
            })
            match_id += 1

    df = pd.DataFrame(fixtures)
    print(f"[DataPipeline] Generated IPL 2026 schedule with {len(df)} fixtures.")
    return df


# -------------------------------------------------------------
# Data Cleaning & Schema Mapping
# -------------------------------------------------------------
def clean_ipl_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and standardise the IPL dataset."""
    df = df.dropna(subset=["winner", "innings1_score", "innings2_score"])
    df["season"] = df["season"].astype(int)
    df["innings1_score"] = df["innings1_score"].clip(0, 300)
    df["innings2_score"] = df["innings2_score"].clip(0, 300)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.sort_values("date").reset_index(drop=True)
    print(f"[DataPipeline] After cleaning: {len(df)} records.")
    return df


# -------------------------------------------------------------
# SQLite Cache Builder
# -------------------------------------------------------------
def build_sqlite_cache(df: pd.DataFrame, db_path: str) -> None:
    """Persist cleaned data to a high-performance SQLite lookup database."""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    df.to_sql("matches", conn, if_exists="replace", index=False)

    # Create composite index for fast venue + team lookups
    conn.execute("CREATE INDEX IF NOT EXISTS idx_team1_venue ON matches (team1, venue);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_team2_venue ON matches (team2, venue);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_season ON matches (season);")
    conn.commit()
    conn.close()
    print(f"[DataPipeline] SQLite cache written -> {db_path}")


def query_venue_stats(venue: str, db_path: str) -> dict:
    """Retrieve historical win stats for a given venue."""
    conn = sqlite3.connect(db_path)
    df = pd.read_sql(
        "SELECT winner, team1, team2, day_night FROM matches WHERE venue = ?",
        conn, params=(venue,)
    )
    conn.close()
    if df.empty:
        return {"batting_first_wins": 0, "chasing_wins": 0, "day_night_pct": 0.0}

    batting_first_wins = (df["winner"] == df["team1"]).sum()
    chasing_wins = (df["winner"] == df["team2"]).sum()
    dn_pct = df["day_night"].mean()

    return {
        "batting_first_wins": int(batting_first_wins),
        "chasing_wins": int(chasing_wins),
        "day_night_pct": round(float(dn_pct), 3),
        "total_matches": len(df),
    }


# -------------------------------------------------------------
# Main ETL Runner
# -------------------------------------------------------------
def run_pipeline() -> pd.DataFrame:
    """Full ETL: generate -> clean -> cache -> return processed DataFrame."""
    os.makedirs(config.RAW_DIR, exist_ok=True)
    os.makedirs(config.PROCESSED_DIR, exist_ok=True)

    # Generate or load synthetic IPL data
    if os.path.exists(config.RAW_IPL_CSV):
        print(f"[DataPipeline] Loading existing data from {config.RAW_IPL_CSV}")
        df = pd.read_csv(config.RAW_IPL_CSV)
    else:
        df = generate_synthetic_ipl_data(n_matches=1200)
        df.to_csv(config.RAW_IPL_CSV, index=False)
        print(f"[DataPipeline] Saved raw data -> {config.RAW_IPL_CSV}")

    # Generate 2026 schedule
    if not os.path.exists(config.SCHEDULE_CSV):
        sched = generate_ipl2026_schedule()
        sched.to_csv(config.SCHEDULE_CSV, index=False)
        print(f"[DataPipeline] Saved schedule -> {config.SCHEDULE_CSV}")

    df_clean = clean_ipl_data(df)
    build_sqlite_cache(df_clean, config.DB_PATH)

    return df_clean


if __name__ == "__main__":
    run_pipeline()
