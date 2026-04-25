import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from analytics.save_charts import ChartSaver


# Only the relative importance of each factor is a judgment call —
# all actual value ranges come from the database itself.
CRITERIA_WEIGHTS = {
    "avg_temp_c":          0.30,
    "total_precip_mm":     0.25,
    "avg_humidity_pct":    0.15,
    "avg_cloud_cover_pct": 0.15,
    "rainy_days":          0.15,
}

# For each metric, True = lower value is better for tourism
LOWER_IS_BETTER = {
    "avg_temp_c":          False,  # warmer (up to a point) is better
    "total_precip_mm":     True,   # less rain is better
    "avg_humidity_pct":    True,   # less humidity is better
    "avg_cloud_cover_pct": True,   # less cloud is better
    "rainy_days":          True,   # fewer rainy days is better
}


class PrescriptiveAnalytics:

    def __init__(self, db_helper):
        self.db = db_helper

    # ------------------------------------------------------------------ #
    #  Data Loaders                                                        #
    # ------------------------------------------------------------------ #

    def load_month_order(self):
        """
        Pull canonical month ordering from climate_baseline.
        Replaces any hardcoded MONTH_ORDER list.
        """
        cursor = self.db.mydb.cursor(dictionary=True)
        cursor.execute("""
            SELECT month_name
            FROM climate_baseline
            ORDER BY month
        """)
        rows = cursor.fetchall()
        cursor.close()
        return [r["month_name"] for r in rows]

    def load_monthly_averages(self):
        """
        Average each scored metric per calendar month across all historical years.
        SQL ORDER BY month means no hardcoded ordering needed.
        """
        cursor = self.db.mydb.cursor(dictionary=True)
        cursor.execute("""
            SELECT
                month,
                month_name,
                AVG(avg_temp_c)          AS avg_temp_c,
                AVG(total_precip_mm)     AS total_precip_mm,
                AVG(avg_humidity_pct)    AS avg_humidity_pct,
                AVG(avg_cloud_cover_pct) AS avg_cloud_cover_pct,
                AVG(rainy_days)          AS rainy_days
            FROM monthly_historical
            GROUP BY month, month_name
            ORDER BY month
        """)
        rows = cursor.fetchall()
        cursor.close()
        df = pd.DataFrame(rows)
        df[list(CRITERIA_WEIGHTS.keys())] = df[list(CRITERIA_WEIGHTS.keys())].astype(float)
        return df

    def load_data_ranges(self):
        """
        Pull the actual min and max of every scored metric directly from
        monthly_historical. These become the scoring boundaries — no
        hardcoded ideal values anywhere.
        """
        cursor = self.db.mydb.cursor(dictionary=True)
        cursor.execute("""
            SELECT
                MIN(avg_temp_c)          AS temp_min,
                MAX(avg_temp_c)          AS temp_max,
                MIN(total_precip_mm)     AS precip_min,
                MAX(total_precip_mm)     AS precip_max,
                MIN(avg_humidity_pct)    AS humid_min,
                MAX(avg_humidity_pct)    AS humid_max,
                MIN(avg_cloud_cover_pct) AS cloud_min,
                MAX(avg_cloud_cover_pct) AS cloud_max,
                MIN(rainy_days)          AS rainy_min,
                MAX(rainy_days)          AS rainy_max
            FROM monthly_historical
        """)
        row = cursor.fetchone()
        cursor.close()

        return {
            "avg_temp_c":          (float(row["temp_min"]),   float(row["temp_max"])),
            "total_precip_mm":     (float(row["precip_min"]), float(row["precip_max"])),
            "avg_humidity_pct":    (float(row["humid_min"]),  float(row["humid_max"])),
            "avg_cloud_cover_pct": (float(row["cloud_min"]),  float(row["cloud_max"])),
            "rainy_days":          (float(row["rainy_min"]),  float(row["rainy_max"])),
        }

    # ------------------------------------------------------------------ #
    #  Scoring — pure min-max normalisation                               #
    # ------------------------------------------------------------------ #

    def _score_column(self, series, col_min, col_max, lower_is_better):
        """
        Maps each value linearly onto 0–100 using the dataset's own
        min/max as boundaries. No external ideal ranges needed.

          lower_is_better=True  → col_min scores 100, col_max scores 0
          lower_is_better=False → col_max scores 100, col_min scores 0
        """
        rang = col_max - col_min if col_max != col_min else 1.0
        scores = []
        for val in series:
            normalised = (val - col_min) / rang          # 0.0 → 1.0
            s = (1 - normalised) if lower_is_better else normalised
            scores.append(round(max(0.0, min(100.0, s * 100)), 2))
        return scores

    def compute_tourism_scores(self, df, data_ranges):
        df = df.copy()
        total_weight = sum(CRITERIA_WEIGHTS.values())
        df["tourism_score"] = 0.0

        for col, weight in CRITERIA_WEIGHTS.items():
            col_min, col_max   = data_ranges[col]
            lower_is_better    = LOWER_IS_BETTER[col]
            col_scores         = self._score_column(df[col], col_min,
                                                    col_max, lower_is_better)
            df["tourism_score"] += (weight / total_weight) * pd.Series(
                col_scores, index=df.index
            )

        df["tourism_score"]  = df["tourism_score"].round(1)
        df["recommendation"] = df["tourism_score"].apply(self._label)
        return df

    @staticmethod
    def _label(score):
        if score >= 75:
            return "Highly Recommended"
        elif score >= 55:
            return "Recommended"
        elif score >= 35:
            return "Acceptable"
        else:
            return "Not Recommended"

    # ------------------------------------------------------------------ #
    #  Chart 1 — Tourism Score Horizontal Bar                             #
    # ------------------------------------------------------------------ #

    def plot_tourism_score_bar(self, df):
        color_map = {
            "Highly Recommended": "#7ED321",
            "Recommended":        "#F5A623",
            "Acceptable":         "#4A90D9",
            "Not Recommended":    "#D0021B",
        }
        colors = df["recommendation"].map(color_map)

        fig, ax = plt.subplots(figsize=(11, 8))
        bars = ax.barh(df["month_name"], df["tourism_score"],
                       color=colors, edgecolor="white", height=0.65)

        ax.bar_label(bars, labels=[f"{v:.1f}" for v in df["tourism_score"]],
                     padding=5, fontsize=10, fontweight="bold")

        # Threshold reference lines
        for thresh, label, col in [
            (75, "Highly Recommended ▶", "#7ED321"),
            (55, "Recommended ▶",        "#F5A623"),
            (35, "Acceptable ▶",         "#4A90D9"),
        ]:
            ax.axvline(thresh, color=col, linewidth=1.2, linestyle="--", alpha=0.6)
            ax.text(thresh + 0.5, 11.6, label, color=col, fontsize=7, va="top")

        ax.set_xlim(0, 115)
        ax.set_xlabel("Tourism Suitability Score (0–100)", fontsize=11)
        ax.set_title("Prescriptive Analysis: Best Months to Visit Pokhara\n"
                     "(Scored against Pokhara's own historical data)",
                     fontsize=13, fontweight="bold", pad=15)
        ax.invert_yaxis()
        ax.grid(axis="x", linestyle="--", alpha=0.3)

        patches = [mpatches.Patch(color=c, label=l) for l, c in color_map.items()]
        ax.legend(handles=patches, loc="lower right", fontsize=9, framealpha=0.9)

        plt.tight_layout()
        ChartSaver.save_analysis_image(fig, "pres_tourism_score_bar.png")
        plt.show()
        return fig

    # ------------------------------------------------------------------ #
    #  Chart 2 — Per-Factor Heatmap                                       #
    # ------------------------------------------------------------------ #

    def plot_factor_heatmap(self, df, data_ranges):
        df = df.copy().set_index("month_name")

        factor_scores = pd.DataFrame(index=df.index)
        for col in CRITERIA_WEIGHTS:
            col_min, col_max = data_ranges[col]
            factor_scores[col] = self._score_column(
                df[col], col_min, col_max, LOWER_IS_BETTER[col]
            )

        factor_scores.columns = [
            "Temperature", "Precipitation", "Humidity", "Cloud Cover", "Rainy Days"
        ]

        fig, ax = plt.subplots(figsize=(11, 8))
        sns.heatmap(
            factor_scores,
            annot=True, fmt=".0f", cmap="RdYlGn",
            linewidths=0.6, linecolor="white",
            ax=ax, vmin=0, vmax=100,
            cbar_kws={"label": "Score (0 = worst in dataset, 100 = best)", "shrink": 0.8},
            annot_kws={"size": 10, "weight": "bold"}
        )

        ax.set_title("Weather Factor Scores by Month — Tourism Perspective\n"
                     "(Min-max normalised from Pokhara historical data)",
                     fontsize=12, fontweight="bold", pad=15)
        ax.set_xlabel("Weather Factor", fontsize=11)
        ax.set_ylabel("Month", fontsize=11)
        ax.tick_params(axis="x", labelsize=10)
        ax.tick_params(axis="y", labelsize=10, rotation=0)

        plt.tight_layout()
        ChartSaver.save_analysis_image(fig, "pres_factor_heatmap.png")
        plt.show()
        return fig

    # ------------------------------------------------------------------ #
    #  Recommendation Summary                                             #
    # ------------------------------------------------------------------ #

    def print_recommendations(self, df, data_ranges):
        print("\n===== PRESCRIPTIVE SUMMARY — Tourism Recommendations =====")
        print("  Scoring ranges derived from Pokhara historical data:")
        col_labels = {
            "avg_temp_c":          "Avg Temp (°C)",
            "total_precip_mm":     "Precipitation (mm)",
            "avg_humidity_pct":    "Humidity (%)",
            "avg_cloud_cover_pct": "Cloud Cover (%)",
            "rainy_days":          "Rainy Days",
        }
        for col, (lo, hi) in data_ranges.items():
            direction = "lower=better" if LOWER_IS_BETTER[col] else "higher=better"
            print(f"    {col_labels[col]:<22} range [{lo:.1f} – {hi:.1f}]  ({direction})")

        print()
        df_sorted = df.sort_values("tourism_score", ascending=False)
        for _, row in df_sorted.iterrows():
            print(f"  {row['month_name']:<12} Score: {row['tourism_score']:>5.1f}"
                  f"  →  {row['recommendation']}")

        best  = df_sorted.iloc[0]
        worst = df_sorted.iloc[-1]
        top3  = df_sorted.head(3)["month_name"].tolist()
        print(f"\n  ✅ Best month   : {best['month_name']} (score {best['tourism_score']})")
        print(f"  ❌ Avoid        : {worst['month_name']} (score {worst['tourism_score']})")
        print(f"  🏆 Top 3 months : {', '.join(top3)}")
        print("=" * 60)

    # ------------------------------------------------------------------ #
    #  Run                                                                 #
    # ------------------------------------------------------------------ #

    def run(self):
        print("\n>>> Running Prescriptive Analytics...")

        df          = self.load_monthly_averages()
        data_ranges = self.load_data_ranges()
        month_order = self.load_month_order()

        if df.empty:
            print("No monthly data found — skipping prescriptive analytics.")
            return

        # Apply DB-derived month ordering so charts stay Jan → Dec
        df["month_name"] = pd.Categorical(
            df["month_name"], categories=month_order, ordered=True
        )
        df = df.sort_values("month_name").reset_index(drop=True)

        df = self.compute_tourism_scores(df, data_ranges)
        self.print_recommendations(df, data_ranges)
        self.plot_tourism_score_bar(df)
        self.plot_factor_heatmap(df, data_ranges)

        print(">>> Prescriptive Analytics complete.\n")
        return df