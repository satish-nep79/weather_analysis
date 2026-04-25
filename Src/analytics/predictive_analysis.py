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
        df = df.copy()
        df["time_index"] = range(len(df))

        X = df["time_index"].values.reshape(-1, 1)
        y = df["avg_temp_c"].values

        # Fit linear regression to get the overall trend direction
        model = LinearRegression()
        model.fit(X, y)
        trend_line = model.predict(X)

        # Calculate the average temperature for each month (Jan-Dec)
        monthly_avg = df.groupby("month")["avg_temp_c"].mean()

        # Predict next 24 months using monthly average + trend adjustment
        last_year       = int(df["year"].iloc[-1])
        last_month      = int(df["month"].iloc[-1])
        trend_per_month = model.coef_[0]
        future_preds    = []
        future_dates    = []
        for i in range(1, 25):
            raw        = last_month + i
            next_month = ((raw - 1) % 12) + 1
            next_year  = last_year + (raw - 1) // 12
            base_avg   = monthly_avg[next_month]
            predicted  = base_avg + trend_per_month * i
            future_preds.append(round(predicted, 2))
            future_dates.append(pd.Timestamp(year=next_year, month=next_month, day=1))

        # Build historical dates for x-axis
        hist_dates = pd.to_datetime(df["year"].astype(str) + "-" + df["month"].astype(str).str.zfill(2) + "-01")

        # Plot
        fig, ax = plt.subplots(figsize=(18, 5))
        ax.plot(hist_dates, y, color="#4A90D9", linewidth=1.2, alpha=0.6, label="Historical Avg Temp")
        ax.plot(hist_dates, trend_line, color="#F5A623", linewidth=2, linestyle="--", label="Overall Trend")
        # Connect prediction to last historical point so there's no gap
        connect_dates = [hist_dates.iloc[-1]] + future_dates
        connect_preds = [y[-1]] + future_preds
        ax.plot(connect_dates, connect_preds, color="#D0021B", linewidth=2, linestyle="--", label="Predicted (next 24 months)")
        ax.axvline(future_dates[0], color="#D0021B", linewidth=1, linestyle=":", alpha=0.5)
        ax.set_xlim(hist_dates.iloc[0], future_dates[-1] + pd.DateOffset(months=2))

        direction = "rising" if model.coef_[0] > 0 else "falling"
        ax.set_title(f"Temperature Trend & 24-Month Prediction - Pokhara ({direction} trend)", fontsize=13, fontweight="bold")
        ax.set_xlabel("Date")
        ax.set_ylabel("Avg Temperature (C)")
        ax.legend(fontsize=10)
        ax.grid(axis="y", linestyle="--", alpha=0.4)
        fig.autofmt_xdate()
        plt.tight_layout()

        # Save BEFORE show — calling show() clears the figure
        ChartSaver.save_analysis_image(fig, "pred_temperature_trend.png")
        plt.show()
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