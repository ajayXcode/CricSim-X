# CricSim-X 🏏

**Premium IPL Match Intelligence & Analytics Engine**

CricSim-X combines a Monte Carlo simulation engine with a stacking meta-classifier (trained on 18 seasons of IPL ball-by-ball records) to provide real-time win probability, predictive analytics, and franchise-level strategy.

![CricSim-X Dashboard Preview](https://img.shields.io/badge/UI-Premium_Dark_Theme-F0A500?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-00C9A7?style=for-the-badge)

## 🌟 Key Features
- **Live Match Simulator:** Calculates real-time win probabilities based on current match state (Runs, Wickets, Balls remaining, Team, and Venue) using a custom Win Probability Index (WPI) and Required Run Rate (RRR) decay formula.
- **Machine Learning Engine:** Ensembles Random Forest, XGBoost, LightGBM, ExtraTrees, and Neural Networks, achieving an AUC-ROC score of **0.7054** on a robust test set of 1,201 IPL match records.
- **Team Analytics:** Radar charts displaying franchise strengths across 6 metrics (Batting, Bowling, Fielding, Form, Powerplay, Death Overs) alongside Exponential Moving Average (EMA) form trends.
- **Venue Insights:** Data-driven toss impact analysis (Bat First vs Chasing success rates) across 10 major Indian cricket stadiums.
- **Fixture Predictions:** Predictive outcome generator for upcoming IPL matches with generated confidence intervals.

## 🏗 Architecture
- **Backend / Pipeline:** Python (Pandas, Scikit-learn, SQLite, Monte Carlo Markov Chain). Modular structure handling ETL (`data_pipeline.py`), Feature Engineering (`feature_engineering.py`), and Model Training (`model_factory.py`).
- **Frontend / Dashboard:** Pure HTML5, Vanilla CSS3 (Custom Design System using `Sora` font), and Vanilla JavaScript.
- **Visualizations:** Chart.js implementation for fully responsive Gauge, Radar, Line, and Bar charts without heavy UI frameworks.

## 🚀 Setup and Usage

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/cricsim-x.git
   cd cricsim-x
   ```

2. **Launch the Dashboard:**
   Simply open the `dashboard/index.html` file in any modern web browser. No local web server is strictly required for the UI, as it runs locally.

3. **Run the Backend Pipeline (Optional):**
   To re-train the models or re-run predictions for new fixtures, run the Python CLI orchestration:
   ```bash
   python main.py --mode all
   ```
   *Requires Python 3.8+ and standard ML libraries (`pandas`, `numpy`, `scikit-learn`, `lightgbm`, `xgboost`).*

## 🎨 UI/UX Philosophy
The dashboard ditches generic glassmorphism and cluttered borders for a highly focused, premium editorial look inspired by the official IPL brand and high-end sports analytics platforms. It utilizes a striking Gold (`#F0A500`), Teal (`#00C9A7`), and True Black (`#06060A`) palette.
