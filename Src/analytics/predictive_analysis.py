import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from analytics.save_charts import ChartSaver


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

    def plot_temperature_trend(self, df):
        # Create a simple time index (0, 1, 2, ... for each month)
        df = df.copy()
        df["time_index"] = range(len(df))

        X = df["time_index"].values.reshape(-1, 1)
        y = df["avg_temp_c"].values

        # Train a simple linear regression model
        model = LinearRegression()
        model.fit(X, y)
        trend_line = model.predict(X)

        # Predict the next 12 months
        last_index = df["time_index"].max()
        future_indices = np.arange(last_index + 1, last_index + 13).reshape(-1, 1)
        future_preds   = model.predict(future_indices)

        # Build dates for the x-axis
        hist_dates   = pd.to_datetime(df["year"].astype(str) + "-" + df["month"].astype(str).str.zfill(2) + "-01")
        last_year    = df["year"].iloc[-1]
        last_month   = df["month"].iloc[-1]
        future_dates = pd.date_range(
            start=pd.Timestamp(year=last_year, month=last_month, day=1) + pd.DateOffset(months=1),
            periods=12,
            freq="MS"
        )

        # Plot
        fig, ax = plt.subplots(figsize=(14, 5))
        ax.plot(hist_dates, y, color="#4A90D9", linewidth=1.2, alpha=0.6, label="Historical Avg Temp")
        ax.plot(hist_dates, trend_line, color="#F5A623", linewidth=2, linestyle="--", label="Trend Line")
        ax.plot(future_dates, future_preds, color="#D0021B", linewidth=2, linestyle="-.", label="Predicted (next 12 months)")
        ax.axvline(future_dates[0], color="#D0021B", linewidth=1, linestyle=":", alpha=0.5)

        direction = "rising" if model.coef_[0] > 0 else "falling"
        ax.set_title(f"Temperature Trend & 12-Month Prediction — Pokhara  ({direction} trend)", fontsize=13, fontweight="bold")
        ax.set_xlabel("Date")
        ax.set_ylabel("Avg Temperature (°C)")
        ax.legend(fontsize=10)
        ax.grid(axis="y", linestyle="--", alpha=0.4)
        fig.autofmt_xdate()
        plt.tight_layout()
        plt.show()
        ChartSaver.save_analysis_image(fig, "pred_temperature_trend.png")
        return fig

    def run(self):
        print("\n>>> Running Predictive Analytics...")
        df = self.load_historical()

        if df.empty:
            print("No historical data found.")
            return

        self.plot_temperature_trend(df)
        print(">>> Predictive Analytics complete.\n")
        return df