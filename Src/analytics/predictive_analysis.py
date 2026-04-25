import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from analytics.analysis_exporter import AnalysisExporter


class PredictiveAnalytics:

    def __init__(self, db_helper):
        self.db = db_helper

    def load_historical(self):
        cursor = self.db.mydb.cursor(dictionary=True)
        cursor.execute("""
            SELECT year, month, month_name, avg_temp_c
            FROM monthly_historical
            ORDER BY year, month
        """)
        rows = cursor.fetchall()
        cursor.close()
        df = pd.DataFrame(rows)
        df["avg_temp_c"] = df["avg_temp_c"].astype(float)
        return df

    def load_forecast(self):
        cursor = self.db.mydb.cursor(dictionary=True)
        cursor.execute("""
            SELECT forecast_date, month, avg_temp_c, precip_mm,
                   precip_probability_pct, weather_description
            FROM daily_forecast
            ORDER BY forecast_date
        """)
        rows = cursor.fetchall()
        cursor.close()
        df = pd.DataFrame(rows)
        if not df.empty:
            df["avg_temp_c"]             = df["avg_temp_c"].astype(float)
            df["precip_mm"]              = df["precip_mm"].astype(float)
            df["precip_probability_pct"] = df["precip_probability_pct"].astype(int)
            df["forecast_date"]          = pd.to_datetime(df["forecast_date"])
        return df

    def plot_forecast_vs_baseline(self, df_hist, df_forecast):
        monthly_avg = df_hist.groupby("month")["avg_temp_c"].mean()

        df_forecast = df_forecast.copy()
        df_forecast["historical_avg"] = df_forecast["month"].map(monthly_avg)
        df_forecast["anomaly"]        = (df_forecast["avg_temp_c"] - df_forecast["historical_avg"]).round(2)

        fig, axes = plt.subplots(2, 1, figsize=(14, 8))

        ax1 = axes[0]
        ax1.plot(df_forecast["forecast_date"], df_forecast["avg_temp_c"],
                 color="#D0021B", linewidth=2, marker="o", markersize=5, label="API Forecast Temp")
        ax1.plot(df_forecast["forecast_date"], df_forecast["historical_avg"],
                 color="#4A90D9", linewidth=2, linestyle="--", label="15-Year Historical Average")
        ax1.fill_between(df_forecast["forecast_date"],
                         df_forecast["historical_avg"], df_forecast["avg_temp_c"],
                         where=df_forecast["avg_temp_c"] >= df_forecast["historical_avg"],
                         alpha=0.15, color="#D0021B", label="Above Normal")
        ax1.fill_between(df_forecast["forecast_date"],
                         df_forecast["historical_avg"], df_forecast["avg_temp_c"],
                         where=df_forecast["avg_temp_c"] < df_forecast["historical_avg"],
                         alpha=0.15, color="#4A90D9", label="Below Normal")
        ax1.set_title("API Forecast vs 15-Year Historical Baseline - Pokhara", fontsize=13, fontweight="bold")
        ax1.set_ylabel("Temperature (C)")
        ax1.legend(fontsize=9)
        ax1.grid(axis="y", linestyle="--", alpha=0.4)

        ax2 = axes[1]
        bar_colors = ["#7ED321" if p < 40 else "#F5A623" if p < 70 else "#D0021B"
                      for p in df_forecast["precip_probability_pct"]]
        ax2.bar(df_forecast["forecast_date"], df_forecast["precip_probability_pct"],
                color=bar_colors, width=0.6)
        ax2.axhline(70, color="#D0021B", linewidth=1, linestyle="--", alpha=0.6, label="High Risk (70%)")
        ax2.set_ylabel("Precipitation Probability (%)")
        ax2.set_xlabel("Date")
        ax2.set_title("Forecasted Precipitation Probability", fontsize=11, fontweight="bold")
        ax2.set_ylim(0, 110)
        ax2.legend(fontsize=9)
        ax2.grid(axis="y", linestyle="--", alpha=0.4)

        fig.autofmt_xdate()
        plt.tight_layout()
        AnalysisExporter.save_image(fig, "pred_forecast_vs_baseline.png")
        plt.show()
        return fig, df_forecast

    def print_forecast_summary(self, df_forecast):
        if df_forecast.empty:
            print("  No API forecast data available.")
            return

        print("\n--- API FORECAST vs HISTORICAL BASELINE ---")
        print(f"  {'Date':<14} {'Forecast':>10} {'Historical':>12} {'Anomaly':>10} {'Rain%':>7}  Decision")
        print("  " + "-" * 75)

        for _, row in df_forecast.iterrows():
            date    = str(row["forecast_date"])[:10]
            temp    = row["avg_temp_c"]
            base    = row["historical_avg"]
            anomaly = row["anomaly"]
            prob    = row["precip_probability_pct"]
            desc    = row["weather_description"]

            if anomaly > 1.5:
                anomaly_flag = "WARMER than normal"
            elif anomaly < -1.5:
                anomaly_flag = "COOLER than normal"
            else:
                anomaly_flag = "Normal range"

            if prob > 70 or row["precip_mm"] > 10:
                decision = "Advise trekkers to postpone"
            elif anomaly > 2:
                decision = "Heat advisory — early morning activities only"
            else:
                decision = "Good conditions for outdoor activities"

            print(f"  {date:<14} {temp:>8.1f}C  {base:>10.1f}C  {anomaly:>+8.1f}C  {prob:>5}%  {decision}")
            print(f"  {'':14} {desc}")

        avg_anomaly    = df_forecast["anomaly"].mean()
        high_rain_days = (df_forecast["precip_probability_pct"] > 70).sum()
        print(f"\n  Overall: Forecast is {avg_anomaly:+.1f}C vs historical average")
        print(f"  High rain risk days: {high_rain_days} out of {len(df_forecast)} forecast days")
        print()

    def run(self):
        print("\n>>> Running Predictive Analytics...")

        df_hist     = self.load_historical()
        df_forecast = self.load_forecast()

        if df_hist.empty:
            print("No historical data found.")
            return

        if df_forecast.empty:
            print("No API forecast data found.")
            return

        fig, df_forecast_with_baseline = self.plot_forecast_vs_baseline(df_hist, df_forecast)
        self.print_forecast_summary(df_forecast_with_baseline)

        print(">>> Predictive Analytics complete.\n")
        return df_hist