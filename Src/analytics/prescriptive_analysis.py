import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from analytics.save_charts import ChartSaver


class PrescriptiveAnalytics:

    def __init__(self, db_helper):
        self.db = db_helper

    def load_monthly_averages(self):
        cursor = self.db.mydb.cursor(dictionary=True)
        cursor.execute("""
            SELECT
                month,
                month_name,
                AVG(avg_temp_c)          AS avg_temp_c,
                AVG(total_precip_mm)     AS total_precip_mm,
                AVG(avg_humidity_pct)    AS avg_humidity_pct,
                AVG(rainy_days)          AS rainy_days
            FROM monthly_historical
            GROUP BY month, month_name
            ORDER BY month
        """)
        rows = cursor.fetchall()
        cursor.close()
        df = pd.DataFrame(rows)
        df["avg_temp_c"]      = df["avg_temp_c"].astype(float)
        df["total_precip_mm"] = df["total_precip_mm"].astype(float)
        df["avg_humidity_pct"]= df["avg_humidity_pct"].astype(float)
        df["rainy_days"]      = df["rainy_days"].astype(float)
        return df

    def score_month(self, row):
        score = 0

        # Temperature: 15–25°C is ideal for tourists
        if 15 <= row["avg_temp_c"] <= 25:
            score += 30
        elif 10 <= row["avg_temp_c"] < 15 or 25 < row["avg_temp_c"] <= 30:
            score += 15

        # Precipitation: less rain is better
        if row["total_precip_mm"] < 50:
            score += 30
        elif row["total_precip_mm"] < 150:
            score += 20
        elif row["total_precip_mm"] < 300:
            score += 10

        # Humidity: lower is more comfortable
        if row["avg_humidity_pct"] < 65:
            score += 20
        elif row["avg_humidity_pct"] < 80:
            score += 10

        # Rainy days: fewer is better
        if row["rainy_days"] < 5:
            score += 20
        elif row["rainy_days"] < 10:
            score += 10

        return score

    def get_recommendation(self, score):
        if score >= 75:
            return "Highly Recommended"
        elif score >= 50:
            return "Recommended"
        elif score >= 30:
            return "Acceptable"
        else:
            return "Not Recommended"

    def plot_tourism_score_bar(self, df):
        color_map = {
            "Highly Recommended": "#7ED321",
            "Recommended":        "#F5A623",
            "Acceptable":         "#4A90D9",
            "Not Recommended":    "#D0021B",
        }
        colors = df["recommendation"].map(color_map)

        fig, ax = plt.subplots(figsize=(11, 7))
        bars = ax.barh(df["month_name"], df["score"], color=colors, edgecolor="white", height=0.6)
        ax.bar_label(bars, labels=[f"{v}" for v in df["score"]], padding=5, fontsize=10, fontweight="bold")

        ax.set_xlim(0, 115)
        ax.set_xlabel("Tourism Suitability Score (0–100)", fontsize=11)
        ax.set_title("Best Months to Visit Pokhara — Tourism Suitability Score", fontsize=13, fontweight="bold")
        ax.invert_yaxis()
        ax.grid(axis="x", linestyle="--", alpha=0.3)

        patches = [mpatches.Patch(color=c, label=l) for l, c in color_map.items()]
        ax.legend(handles=patches, loc="lower right", fontsize=9)

        plt.tight_layout()
        plt.show()
        ChartSaver.save_analysis_image(fig, "pres_tourism_score_bar.png")
        return fig

    def run(self):
        print("\n>>> Running Prescriptive Analytics...")
        df = self.load_monthly_averages()

        if df.empty:
            print("No monthly data found.")
            return

        df["score"]          = df.apply(self.score_month, axis=1)
        df["recommendation"] = df["score"].apply(self.get_recommendation)

        print("\n===== PRESCRIPTIVE SUMMARY — Best Months to Visit Pokhara =====")
        df_sorted = df.sort_values("score", ascending=False)
        for _, row in df_sorted.iterrows():
            print(f"  {row['month_name']:<12}  Score: {row['score']:>3}  →  {row['recommendation']}")
        best = df_sorted.iloc[0]
        worst = df_sorted.iloc[-1]
        print(f"\n  ✅ Best month  : {best['month_name']} (score {best['score']})")
        print(f"  ❌ Avoid       : {worst['month_name']} (score {worst['score']})")
        print("=" * 60 + "\n")

        self.plot_tourism_score_bar(df)
        print(">>> Prescriptive Analytics complete.\n")
        return df