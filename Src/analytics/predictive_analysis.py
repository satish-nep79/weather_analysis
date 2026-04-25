import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from sklearn.linear_model import LinearRegression
from analytics.save_charts import ChartSaver


class PredictiveAnalytics:

    def __init__(self, db_helper):
        self.db = db_helper

    # ------------------------------------------------------------------ #
    #  Data Loaders                                                        #
    # ------------------------------------------------------------------ #

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
        """Load daily forecast records (keep daily granularity for richer chart)."""
        cursor = self.db.mydb.cursor(dictionary=True)
        cursor.execute("""
            SELECT forecast_date, year, month, month_name, avg_temp_c
            FROM daily_forecast
            ORDER BY forecast_date
        """)
        rows = cursor.fetchall()
        cursor.close()
        df = pd.DataFrame(rows)
        if not df.empty:
            df["avg_temp_c"]    = df["avg_temp_c"].astype(float)
            df["forecast_date"] = pd.to_datetime(df["forecast_date"])
        return df

    # ------------------------------------------------------------------ #
    #  Model — Linear Regression + Fourier seasonal terms                 #
    # ------------------------------------------------------------------ #

    def _build_features(self, time_index_series):
        """
        Feature matrix:
          t         — linear trend
          sin/cos   — annual (12-month) and semi-annual (6-month) cycles
        """
        t     = time_index_series.values.astype(float)
        sin12 = np.sin(2 * np.pi * t / 12)
        cos12 = np.cos(2 * np.pi * t / 12)
        sin6  = np.sin(2 * np.pi * t / 6)
        cos6  = np.cos(2 * np.pi * t / 6)
        return np.column_stack([t, sin12, cos12, sin6, cos6])

    def train_model(self, df):
        df = df.copy()
        df["time_index"] = (df["year"] - df["year"].min()) * 12 + (df["month"] - 1)
        X = self._build_features(df["time_index"])
        y = df["avg_temp_c"].values
        model = LinearRegression()
        model.fit(X, y)
        return model, df

    def predict_future(self, model, last_time_index, base_year, n_months=24):
        future_indices = np.arange(last_time_index + 1,
                                   last_time_index + 1 + n_months)
        X_future = self._build_features(pd.Series(future_indices))
        preds    = model.predict(X_future)
        dates    = [pd.Timestamp(year=base_year + i // 12, month=(i % 12) + 1, day=1)
                    for i in future_indices]
        return future_indices, preds, dates

    def predict_for_dates(self, model, df_hist, df_forecast):
        base_year  = df_hist["year"].min()
        time_index = (df_forecast["year"] - base_year) * 12 + (df_forecast["month"] - 1)
        X = self._build_features(time_index)
        return model.predict(X)

    # ------------------------------------------------------------------ #
    #  Chart 1 — Temperature Trend & 24-Month Prediction                  #
    # ------------------------------------------------------------------ #

    def plot_temperature_trend(self, df, model):
        df        = df.copy()
        base_year = df["year"].min()
        df["time_index"] = (df["year"] - base_year) * 12 + (df["month"] - 1)

        X_hist = self._build_features(df["time_index"])
        y_fit  = model.predict(X_hist)

        future_idx, future_preds, future_dates = self.predict_future(
            model, df["time_index"].max(), base_year
        )

        hist_dates = pd.to_datetime(
            df["year"].astype(str) + "-" + df["month"].astype(str).str.zfill(2) + "-01"
        )

        fig, ax = plt.subplots(figsize=(15, 6))

        ax.plot(hist_dates, df["avg_temp_c"],
                color="#4A90D9", linewidth=1.2, alpha=0.6, label="Historical Avg Temp")
        ax.plot(hist_dates, y_fit,
                color="#F5A623", linewidth=2.2, linestyle="--", label="Seasonal Regression Fit")
        ax.plot(future_dates, future_preds,
                color="#D0021B", linewidth=2.2, linestyle="-.", label="Predicted (next 24 months)")

        ax.axvspan(future_dates[0], future_dates[-1],
                   alpha=0.07, color="#D0021B", label="_nolegend_")
        ax.axvline(future_dates[0], color="#D0021B", linewidth=1, linestyle=":", alpha=0.6)

        # Annotate predicted peak & trough
        peak_i   = int(np.argmax(future_preds))
        trough_i = int(np.argmin(future_preds))
        ax.annotate(f"Peak {future_preds[peak_i]:.1f}°C",
                    xy=(future_dates[peak_i], future_preds[peak_i]),
                    xytext=(10, 10), textcoords="offset points", fontsize=8, color="#D0021B",
                    arrowprops=dict(arrowstyle="->", color="#D0021B", lw=0.8))
        ax.annotate(f"Trough {future_preds[trough_i]:.1f}°C",
                    xy=(future_dates[trough_i], future_preds[trough_i]),
                    xytext=(10, -25), textcoords="offset points", fontsize=8, color="#D0021B",
                    arrowprops=dict(arrowstyle="->", color="#D0021B", lw=0.8))

        ax.set_title("Temperature Trend & 24-Month Seasonal Prediction — Pokhara",
                     fontsize=14, fontweight="bold", pad=15)
        ax.set_xlabel("Date", fontsize=11)
        ax.set_ylabel("Avg Temperature (°C)", fontsize=11)
        ax.legend(fontsize=10, loc="upper left")
        ax.grid(axis="y", linestyle="--", alpha=0.4)
        fig.autofmt_xdate()
        plt.tight_layout()

        ChartSaver.save_analysis_image(fig, "pred_temperature_trend.png")
        plt.show()
        return fig

    # ------------------------------------------------------------------ #
    #  Chart 2 — API Forecast vs Model Prediction                         #
    # ------------------------------------------------------------------ #

    def plot_forecast_vs_predicted(self, df_hist, model, df_forecast):
        if df_forecast.empty:
            print("No forecast data available — skipping forecast vs predicted chart.")
            return

        df_fc = df_forecast.copy()
        df_fc["predicted_temp"] = self.predict_for_dates(model, df_hist, df_fc)
        df_fc["error"]          = df_fc["avg_temp_c"] - df_fc["predicted_temp"]

        fig = plt.figure(figsize=(14, 8))
        gs  = gridspec.GridSpec(2, 1, height_ratios=[3, 1], hspace=0.4)

        # Top: temperature lines
        ax1 = fig.add_subplot(gs[0])
        ax1.plot(df_fc["forecast_date"], df_fc["avg_temp_c"],
                 marker="o", markersize=4, color="#4A90D9",
                 linewidth=2, label="API Forecast Temp")
        ax1.plot(df_fc["forecast_date"], df_fc["predicted_temp"],
                 marker="s", markersize=4, color="#D0021B",
                 linewidth=2, linestyle="--", label="Model Predicted Temp")
        ax1.fill_between(df_fc["forecast_date"],
                         df_fc["avg_temp_c"], df_fc["predicted_temp"],
                         alpha=0.12, color="#7ED321", label="Difference")

        # Annotate max divergence
        max_i = df_fc["error"].abs().idxmax()
        ax1.annotate(
            f"Max diff: {df_fc.loc[max_i, 'error']:.1f}°C",
            xy=(df_fc.loc[max_i, "forecast_date"], df_fc.loc[max_i, "avg_temp_c"]),
            xytext=(10, 15), textcoords="offset points", fontsize=8,
            arrowprops=dict(arrowstyle="->", lw=0.8)
        )

        ax1.set_title("API Daily Forecast vs Seasonal Model Prediction — Upcoming Period",
                      fontsize=13, fontweight="bold")
        ax1.set_ylabel("Temperature (°C)", fontsize=10)
        ax1.legend(fontsize=9)
        ax1.grid(axis="y", linestyle="--", alpha=0.4)
        fig.autofmt_xdate()

        # Bottom: error bars
        ax2 = fig.add_subplot(gs[1])
        bar_colors = ["#D0021B" if e > 0 else "#4A90D9" for e in df_fc["error"]]
        ax2.bar(df_fc["forecast_date"], df_fc["error"],
                color=bar_colors, width=1.0, alpha=0.8)
        ax2.axhline(0, color="black", linewidth=0.8)
        ax2.set_ylabel("Error (°C)", fontsize=9)
        ax2.set_xlabel("Date", fontsize=10)
        ax2.set_title("Forecast − Prediction Residual", fontsize=10)
        ax2.grid(axis="y", linestyle="--", alpha=0.3)
        fig.autofmt_xdate()

        plt.tight_layout()
        ChartSaver.save_analysis_image(fig, "pred_forecast_vs_predicted.png")
        plt.show()
        return fig

    # ------------------------------------------------------------------ #
    #  Run                                                                 #
    # ------------------------------------------------------------------ #

    def run(self):
        print("\n>>> Running Predictive Analytics...")

        df_hist     = self.load_historical()
        df_forecast = self.load_forecast()

        if df_hist.empty:
            print("No historical data found — cannot train model.")
            return

        model, df_hist = self.train_model(df_hist)

        slope     = model.coef_[0]
        direction = "rising" if slope > 0 else "falling"
        print(f"  Trend slope : {slope:.5f}°C/month ({direction})")
        print(f"  Records used: {len(df_hist)} monthly observations")

        self.plot_temperature_trend(df_hist, model)
        self.plot_forecast_vs_predicted(df_hist, model, df_forecast)

        print(">>> Predictive Analytics complete.\n")
        return model, df_hist, df_forecast