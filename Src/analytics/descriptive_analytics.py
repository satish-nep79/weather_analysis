import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from analytics.save_charts import ChartSaver
from constants import Constants

class DescriptiveAnalytics:

    def __init__(self, db_helper):
        self.db = db_helper

    def load_data(self):
        """Pull monthly_historical from DB into a DataFrame."""
        cursor = self.db.mydb.cursor(dictionary=True)
        cursor.execute("""
            SELECT mh.*, s.season_name
            FROM monthly_historical mh
            LEFT JOIN seasons s ON mh.season_id = s.season_id
            ORDER BY year, month
        """)
        rows = cursor.fetchall()
        cursor.close()
        return pd.DataFrame(rows)

    def summary_statistics(self, df):
        """Print key summary stats — answers basic 'what happened' questions."""
        print("\n===== DESCRIPTIVE SUMMARY =====")
        print(f"Period         : {df['year'].min()} – {df['year'].max()}")
        print(f"Hottest month  : {df.loc[df['max_temp_c'].idxmax(), 'month_name']} "
              f"{df.loc[df['max_temp_c'].idxmax(), 'year']} "
              f"({df['max_temp_c'].max()}°C)")
        print(f"Coldest month  : {df.loc[df['min_temp_c'].idxmin(), 'month_name']} "
              f"{df.loc[df['min_temp_c'].idxmin(), 'year']} "
              f"({df['min_temp_c'].min()}°C)")
        print(f"Wettest month  : {df.loc[df['total_precip_mm'].idxmax(), 'month_name']} "
              f"{df.loc[df['total_precip_mm'].idxmax(), 'year']} "
              f"({df['total_precip_mm'].max()} mm)")
        print(f"Driest month   : {df.loc[df['total_precip_mm'].idxmin(), 'month_name']} "
              f"{df.loc[df['total_precip_mm'].idxmin(), 'year']} "
              f"({df['total_precip_mm'].min()} mm)")

        print("\n--- Seasonal Averages ---")
        seasonal = df.groupby("season_name").agg(
            avg_temp   = ("avg_temp_c",      "mean"),
            avg_precip = ("total_precip_mm", "mean"),
            avg_humid  = ("avg_humidity_pct","mean"),
            avg_cloud  = ("avg_cloud_cover_pct", "mean")
        ).round(2)
        print(seasonal.to_string())
        return seasonal

    def plot_monthly_temperature(self, df):
        """Bar chart — average temperature per month across all years."""
        monthly = df.groupby(["month", "month_name"])["avg_temp_c"].mean().reset_index()
        monthly = monthly.sort_values("month")

        fig, ax = plt.subplots(figsize=(12, 5))
        bars = ax.bar(monthly["month_name"], monthly["avg_temp_c"],
                      color=sns.color_palette("coolwarm", 12))
        ax.set_title(f"Average Monthly Temperature ({df['year'].min()}–{df['year'].max()})", fontsize=14)
        ax.set_xlabel("Month")
        ax.set_ylabel("Avg Temperature (°C)")
        ax.bar_label(bars, fmt="%.1f°", padding=3, fontsize=8)
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.plot()  # Ensure the plot is rendered before saving
        plt.show()  # Show the plot before saving
        ChartSaver.save_analysis_image(fig, "desc_monthly_temperature.png")
        return fig

    def plot_monthly_precipitation(self, df):
        """Bar chart — average monthly precipitation."""
        monthly = df.groupby(["month", "month_name"])["total_precip_mm"].mean().reset_index()
        monthly = monthly.sort_values("month")

        fig, ax = plt.subplots(figsize=(12, 5))
        bars = ax.bar(monthly["month_name"], monthly["total_precip_mm"],
                      color=sns.color_palette("Blues_d", 12))
        ax.set_title(f"Average Monthly Precipitation ({df['year'].min()}–{df['year'].max()})", fontsize=14)
        ax.set_xlabel("Month")
        ax.set_ylabel("Total Precipitation (mm)")
        ax.bar_label(bars, fmt="%.0f mm", padding=3, fontsize=8)
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.plot()  # Ensure the plot is rendered before saving
        plt.show()  # Show the plot before saving
        ChartSaver.save_analysis_image(fig, "desc_monthly_precipitation.png")

    def plot_seasonal_comparison(self, df):
        """Grouped bar chart — seasonal averages for temp, precip, humidity."""
        seasonal = df.groupby("season_name").agg(
            avg_temp   = ("avg_temp_c",          "mean"),
            avg_precip = ("total_precip_mm",      "mean"),
            avg_humid  = ("avg_humidity_pct",     "mean")
        ).round(2)
        seasonal = seasonal.reindex(Constants.SEASON_ORDER).reset_index()

        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        metrics = [
            ("avg_temp",   "Avg Temperature (°C)",    "Oranges"),
            ("avg_precip", "Avg Precipitation (mm)",  "Blues"),
            ("avg_humid",  "Avg Humidity (%)",         "Greens"),
        ]
        for ax, (col, label, palette) in zip(axes, metrics):
            colors = [Constants.SEASON_COLORS[s] for s in seasonal["season_name"]]
            bars = ax.bar(seasonal["season_name"], seasonal[col], color=colors)
            ax.set_title(label, fontsize=12)
            ax.set_xlabel("")
            ax.bar_label(bars, fmt="%.1f", padding=3, fontsize=9)
            plt.setp(ax.get_xticklabels(), rotation=20, ha="right")

        fig.suptitle(f"Seasonal Weather Comparison ({df['year'].min()}–{df['year'].max()})", fontsize=14, y=1.02)
        plt.tight_layout()
        plt.subplots_adjust(top=0.9)
        plt.plot()  # Ensure the plot is rendered before saving
        plt.show()  # Show the plot before saving
        ChartSaver.save_analysis_image(fig, "desc_seasonal_comparison.png")

    def plot_heatmap(self, df):
        """Heatmap — average temperature by month and year."""
        pivot = df.pivot_table(
            index="year", columns="month", values="avg_temp_c", aggfunc="mean"
        )
        pivot.columns = ["Jan","Feb","Mar","Apr","May","Jun",
                         "Jul","Aug","Sep","Oct","Nov","Dec"]

        fig, ax = plt.subplots(figsize=(14, 7))
        sns.heatmap(pivot, annot=True, fmt=".1f", cmap="RdYlBu_r",
                    linewidths=0.5, ax=ax, cbar_kws={"label": "°C"})
        ax.set_title(f"Monthly Average Temperature Heatmap (°C) — {df['year'].min()} to {df['year'].max()}", fontsize=14)
        ax.set_xlabel("Month")
        ax.set_ylabel("Year")
        plt.tight_layout()
        plt.plot()  # Ensure the plot is rendered before saving
        plt.show()  # Show the plot before saving
        ChartSaver.save_analysis_image(fig, "desc_temp_heatmap.png")

    def run(self):
        print("\n>>> Running Descriptive Analytics...")
        df = self.load_data()
        self.summary_statistics(df)
        self.plot_monthly_temperature(df)
        self.plot_monthly_precipitation(df)
        self.plot_seasonal_comparison(df)
        self.plot_heatmap(df)
        print(">>> Descriptive Analytics complete.\n")
        return df