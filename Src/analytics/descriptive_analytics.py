import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from analytics.save_charts import ChartSaver


class DescriptiveAnalytics:

    def __init__(self, db_helper):
        self.db = db_helper

    def load_data(self):
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
        print("\n===== DESCRIPTIVE SUMMARY =====")
        print(f"Period        : {df['year'].min()} – {df['year'].max()}")
        print(f"Hottest month : {df.loc[df['max_temp_c'].idxmax(), 'month_name']} "
              f"{df.loc[df['max_temp_c'].idxmax(), 'year']} "
              f"({df['max_temp_c'].max()}°C)")
        print(f"Coldest month : {df.loc[df['min_temp_c'].idxmin(), 'month_name']} "
              f"{df.loc[df['min_temp_c'].idxmin(), 'year']} "
              f"({df['min_temp_c'].min()}°C)")
        print(f"Wettest month : {df.loc[df['total_precip_mm'].idxmax(), 'month_name']} "
              f"{df.loc[df['total_precip_mm'].idxmax(), 'year']} "
              f"({df['total_precip_mm'].max()} mm)")
        print(f"Driest month  : {df.loc[df['total_precip_mm'].idxmin(), 'month_name']} "
              f"{df.loc[df['total_precip_mm'].idxmin(), 'year']} "
              f"({df['total_precip_mm'].min()} mm)")
        print("================================\n")

    def plot_monthly_temperature(self, df):
        monthly = df.groupby(["month", "month_name"])["avg_temp_c"].mean().reset_index()
        monthly = monthly.sort_values("month")

        fig, ax = plt.subplots(figsize=(12, 5))
        bars = ax.bar(monthly["month_name"], monthly["avg_temp_c"],
                      color=sns.color_palette("coolwarm", 12))
        ax.set_title(f"Average Monthly Temperature ({df['year'].min()}–{df['year'].max()})", fontsize=14)
        ax.set_xlabel("Month")
        ax.set_ylabel("Avg Temperature (°C)")
        ax.bar_label(bars, fmt="%.1f°", padding=3, fontsize=9)
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.show()
        ChartSaver.save_analysis_image(fig, "desc_monthly_temperature.png")
        return fig

    def run(self):
        print("\n>>> Running Descriptive Analytics...")
        df = self.load_data()
        self.summary_statistics(df)
        self.plot_monthly_temperature(df)
        print(">>> Descriptive Analytics complete.\n")
        return df