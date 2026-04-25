import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from analytics.save_charts import ChartSaver


class KPIAnalytics:

    def __init__(self, db_helper):
        self.db = db_helper

    def load_historical(self):
        cursor = self.db.mydb.cursor(dictionary=True)
        cursor.execute("""
            SELECT mh.*, s.season_name
            FROM monthly_historical mh
            LEFT JOIN seasons s ON mh.season_id = s.season_id
            ORDER BY year, month
        """)
        rows = cursor.fetchall()
        cursor.close()
        df = pd.DataFrame(rows)
        df["avg_temp_c"]          = df["avg_temp_c"].astype(float)
        df["total_precip_mm"]     = df["total_precip_mm"].astype(float)
        df["avg_humidity_pct"]    = df["avg_humidity_pct"].astype(float)
        df["avg_wind_spd_ms"]     = df["avg_wind_spd_ms"].astype(float)
        df["avg_cloud_cover_pct"] = df["avg_cloud_cover_pct"].astype(float)
        df["rainy_days"]          = df["rainy_days"].astype(float)
        return df

    def compute_and_print_kpis(self, df):
        print("\n===== PROJECT 3 — KPI SUMMARY =====")

        # --- NUMBER KPIs ---
        print("\n-- Number KPIs --")

        avg_temp = round(df["avg_temp_c"].mean(), 2)
        print(f"  Average Temperature       : {avg_temp} C    | Target: >= 18C  | {'Met' if avg_temp >= 18 else 'Not Met'}")

        avg_precip = round(df["total_precip_mm"].mean(), 1)
        print(f"  Avg Monthly Precipitation : {avg_precip} mm  | Target: <= 300mm | {'Met' if avg_precip <= 300 else 'Not Met'}")

        avg_rainy = round(df["rainy_days"].mean(), 1)
        print(f"  Avg Rainy Days per Month  : {avg_rainy} days | Target: <= 12    | {'Met' if avg_rainy <= 12 else 'Not Met'}")

        # --- PROGRESS KPIs ---
        print("\n-- Progress KPIs --")

        dry_months = (df.groupby("month")["total_precip_mm"].mean() < 100).sum()
        pct_dry = round(dry_months / 12 * 100, 1)
        print(f"  % Dry Months (< 100mm)    : {pct_dry}%       | Target: >= 40%   | {'Met' if pct_dry >= 40 else 'Not Met'}")

        good_temp_months = (df.groupby("month")["avg_temp_c"].mean().between(15, 28)).sum()
        pct_good_temp = round(good_temp_months / 12 * 100, 1)
        print(f"  % Comfortable Temp Months : {pct_good_temp}% | Target: >= 50%   | {'Met' if pct_good_temp >= 50 else 'Not Met'}")

        # --- CHANGE KPIs ---
        print("\n-- Change KPIs --")

        annual_temp = df.groupby("year")["avg_temp_c"].mean()
        if len(annual_temp) >= 2:
            years     = annual_temp.index.tolist()
            yoy_temp  = round(((annual_temp.iloc[-1] - annual_temp.iloc[-2]) / annual_temp.iloc[-2]) * 100, 2)
            direction = "up" if yoy_temp > 0 else "down"
            print(f"  YoY Temp Change ({years[-2]} to {years[-1]})  : {direction} {abs(yoy_temp)}% | Target: <= 1%    | {'Met' if abs(yoy_temp) <= 1 else 'Not Met'}")

        annual_precip = df.groupby("year")["total_precip_mm"].sum()
        if len(annual_precip) >= 2:
            years      = annual_precip.index.tolist()
            yoy_precip = round(((annual_precip.iloc[-1] - annual_precip.iloc[-2]) / annual_precip.iloc[-2]) * 100, 2)
            direction  = "up" if yoy_precip > 0 else "down"
            print(f"  YoY Precip Change ({years[-2]} to {years[-1]}): {direction} {abs(yoy_precip)}% | Target: <= 10%   | {'Met' if abs(yoy_precip) <= 10 else 'Not Met'}")

        print("\n===================================\n")

    def plot_correlation_heatmap(self, df):
        cols = ["avg_temp_c", "total_precip_mm", "avg_humidity_pct",
                "avg_wind_spd_ms", "avg_cloud_cover_pct", "rainy_days"]
        corr = df[cols].corr().round(2)
        corr.index   = ["Temp", "Precip", "Humidity", "Wind", "Cloud", "Rainy Days"]
        corr.columns = ["Temp", "Precip", "Humidity", "Wind", "Cloud", "Rainy Days"]

        fig, ax = plt.subplots(figsize=(9, 7))
        sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm",
                    linewidths=0.5, ax=ax, vmin=-1, vmax=1,
                    cbar_kws={"label": "Correlation Coefficient"})
        ax.set_title("Correlation Between Weather Variables - Pokhara", fontsize=13, fontweight="bold")
        plt.tight_layout()
        ChartSaver.save_analysis_image(fig, "kpi_correlation_heatmap.png")
        plt.show()
        return fig

    def run(self):
        print("\n>>> Running KPI Analysis...")
        df = self.load_historical()

        if df.empty:
            print("No historical data found.")
            return

        self.compute_and_print_kpis(df)
        self.plot_correlation_heatmap(df)
        print(">>> KPI Analysis complete.\n")
        return df