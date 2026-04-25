import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from analytics.save_charts import ChartSaver


class KPIAnalytics:

    def __init__(self, db_helper):
        self.db = db_helper

    # ------------------------------------------------------------------ #
    #  Load Data                                                           #
    # ------------------------------------------------------------------ #

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

    # ------------------------------------------------------------------ #
    #  Compute and Print KPIs                                             #
    # ------------------------------------------------------------------ #

    def compute_and_print_kpis(self, df):
        print("\n===== PROJECT 3 — KPI SUMMARY =====")

        # --- NUMBER KPIs ---
        print("\n-- Number KPIs --")

        avg_temp = round(df["avg_temp_c"].mean(), 2)
        print(f"  Average Temperature      : {avg_temp} °C     | Target: >= 18°C  | {'✅ Met' if avg_temp >= 18 else '❌ Not Met'}")

        avg_precip = round(df["total_precip_mm"].mean(), 1)
        print(f"  Avg Monthly Precipitation: {avg_precip} mm   | Target: <= 300mm | {'✅ Met' if avg_precip <= 300 else '❌ Not Met'}")

        avg_rainy = round(df["rainy_days"].mean(), 1)
        print(f"  Avg Rainy Days per Month : {avg_rainy} days  | Target: <= 12    | {'✅ Met' if avg_rainy <= 12 else '❌ Not Met'}")

        # --- PROGRESS KPIs ---
        print("\n-- Progress KPIs --")

        dry_months = (df.groupby("month")["total_precip_mm"].mean() < 100).sum()
        pct_dry = round(dry_months / 12 * 100, 1)
        print(f"  % Dry Months (< 100mm)   : {pct_dry}%        | Target: >= 40%   | {'✅ Met' if pct_dry >= 40 else '❌ Not Met'}")

        good_temp_months = (df.groupby("month")["avg_temp_c"].mean().between(15, 28)).sum()
        pct_good_temp = round(good_temp_months / 12 * 100, 1)
        print(f"  % Comfortable Temp Months: {pct_good_temp}%  | Target: >= 50%   | {'✅ Met' if pct_good_temp >= 50 else '❌ Not Met'}")

        # --- CHANGE KPIs ---
        print("\n-- Change KPIs --")

        annual_temp = df.groupby("year")["avg_temp_c"].mean()
        if len(annual_temp) >= 2:
            years = annual_temp.index.tolist()
            prev_temp = annual_temp.iloc[-2]
            curr_temp = annual_temp.iloc[-1]
            yoy_temp = round(((curr_temp - prev_temp) / prev_temp) * 100, 2)
            direction = "↑" if yoy_temp > 0 else "↓"
            print(f"  YoY Temp Change ({years[-2]}→{years[-1]}): {direction} {abs(yoy_temp)}% | Target: <= 1%    | {'✅ Met' if abs(yoy_temp) <= 1 else '❌ Not Met'}")

        annual_precip = df.groupby("year")["total_precip_mm"].sum()
        if len(annual_precip) >= 2:
            years = annual_precip.index.tolist()
            prev_precip = annual_precip.iloc[-2]
            curr_precip = annual_precip.iloc[-1]
            yoy_precip = round(((curr_precip - prev_precip) / prev_precip) * 100, 2)
            direction = "↑" if yoy_precip > 0 else "↓"
            print(f"  YoY Precip Change ({years[-2]}→{years[-1]}): {direction} {abs(yoy_precip)}% | Target: <= 10%   | {'✅ Met' if abs(yoy_precip) <= 10 else '❌ Not Met'}")

        print("\n===================================\n")

    # ------------------------------------------------------------------ #
    #  Chart 1 — Box Plot by Season (Seaborn)                            #
    # ------------------------------------------------------------------ #

    def plot_seasonal_boxplot(self, df):
        season_order = ["Winter", "Pre-Monsoon", "Monsoon", "Post-Monsoon"]
        palette = {
            "Winter": "#4A90D9", "Pre-Monsoon": "#F5A623",
            "Monsoon": "#7ED321", "Post-Monsoon": "#D0021B"
        }

        fig, axes = plt.subplots(1, 3, figsize=(15, 6))

        sns.boxplot(data=df, x="season_name", y="avg_temp_c",
                    order=season_order, palette=palette, ax=axes[0])
        axes[0].set_title("Temperature by Season (°C)", fontsize=12, fontweight="bold")
        axes[0].set_xlabel("")
        axes[0].set_ylabel("Avg Temperature (°C)", fontsize=10)

        sns.boxplot(data=df, x="season_name", y="total_precip_mm",
                    order=season_order, palette=palette, ax=axes[1])
        axes[1].set_title("Precipitation by Season (mm)", fontsize=12, fontweight="bold")
        axes[1].set_xlabel("")
        axes[1].set_ylabel("Total Precipitation (mm)", fontsize=10)

        sns.boxplot(data=df, x="season_name", y="avg_humidity_pct",
                    order=season_order, palette=palette, ax=axes[2])
        axes[2].set_title("Humidity by Season (%)", fontsize=12, fontweight="bold")
        axes[2].set_xlabel("")
        axes[2].set_ylabel("Avg Humidity (%)", fontsize=10)

        for ax in axes:
            ax.tick_params(axis="x", rotation=15)
            ax.grid(axis="y", linestyle="--", alpha=0.4)

        fig.suptitle("Seasonal Distribution — Box Plots (Pokhara Historical Data)",
                     fontsize=13, fontweight="bold")
        plt.tight_layout()
        plt.plot()
        plt.show()
        
        ChartSaver.save_analysis_image(fig, "kpi_seasonal_boxplot.png")
        return fig

    # ------------------------------------------------------------------ #
    #  Chart 2 — Pair Plot (Seaborn)                                     #
    # ------------------------------------------------------------------ #

    def plot_pairplot(self, df):
        palette = {
            "Winter": "#4A90D9", "Pre-Monsoon": "#F5A623",
            "Monsoon": "#7ED321", "Post-Monsoon": "#D0021B"
        }

        cols = ["avg_temp_c", "total_precip_mm", "avg_humidity_pct",
                "avg_cloud_cover_pct", "season_name"]
        plot_df = df[cols].dropna()
        plot_df = plot_df.rename(columns={
            "avg_temp_c":          "Temp (°C)",
            "total_precip_mm":     "Precip (mm)",
            "avg_humidity_pct":    "Humidity (%)",
            "avg_cloud_cover_pct": "Cloud Cover (%)",
        })

        g = sns.pairplot(plot_df, hue="season_name", palette=palette,
                         diag_kind="kde", plot_kws={"alpha": 0.5, "s": 20})
        g.figure.suptitle("Pair Plot — Weather Variable Correlations by Season",
                           y=1.02, fontsize=13, fontweight="bold")
        plt.tight_layout()
        plt.plot()
        plt.show()
        ChartSaver.save_analysis_image(g.figure, "kpi_pairplot.png")
        
        return g.figure

    # ------------------------------------------------------------------ #
    #  Chart 3 — Correlation Heatmap (Seaborn)                          #
    # ------------------------------------------------------------------ #

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
        ax.set_title("Correlation Matrix — Weather Variables (Pokhara)",
                     fontsize=13, fontweight="bold", pad=15)
        plt.tight_layout()
        plt.plot()
        plt.show()
        ChartSaver.save_analysis_image(fig, "kpi_correlation_heatmap.png")
        return fig

    # ------------------------------------------------------------------ #
    #  Run                                                                #
    # ------------------------------------------------------------------ #

    def run(self):
        print("\n>>> Running KPI Analysis (Project 3)...")

        df = self.load_historical()

        if df.empty:
            print("No historical data found.")
            return

        self.compute_and_print_kpis(df)
        self.plot_seasonal_boxplot(df)
        self.plot_pairplot(df)
        self.plot_correlation_heatmap(df)

        print(">>> KPI Analysis complete.\n")
        return df