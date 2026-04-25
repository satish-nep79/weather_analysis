import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from analytics.analysis_exporter import AnalysisExporter


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

    # Returns a dict of live-computed KPI values so export_kpi_metadata() can use them
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

        yoy_temp_val, yoy_temp_years   = None, ("N/A", "N/A")
        yoy_precip_val, yoy_precip_years = None, ("N/A", "N/A")

        annual_temp = df.groupby("year")["avg_temp_c"].mean()
        if len(annual_temp) >= 2:
            yoy_temp_years = (annual_temp.index[-2], annual_temp.index[-1])
            yoy_temp_val   = round(((annual_temp.iloc[-1] - annual_temp.iloc[-2]) / annual_temp.iloc[-2]) * 100, 2)
            direction      = "up" if yoy_temp_val > 0 else "down"
            print(f"  YoY Temp Change ({yoy_temp_years[0]} to {yoy_temp_years[1]})  : {direction} {abs(yoy_temp_val)}% | Target: <= 1%    | {'Met' if abs(yoy_temp_val) <= 1 else 'Not Met'}")

        annual_precip = df.groupby("year")["total_precip_mm"].sum()
        if len(annual_precip) >= 2:
            yoy_precip_years = (annual_precip.index[-2], annual_precip.index[-1])
            yoy_precip_val   = round(((annual_precip.iloc[-1] - annual_precip.iloc[-2]) / annual_precip.iloc[-2]) * 100, 2)
            direction        = "up" if yoy_precip_val > 0 else "down"
            print(f"  YoY Precip Change ({yoy_precip_years[0]} to {yoy_precip_years[1]}): {direction} {abs(yoy_precip_val)}% | Target: <= 10%   | {'Met' if abs(yoy_precip_val) <= 10 else 'Not Met'}")

        print("\n===================================\n")

        # Return live values for the metadata exporter
        return {
            "avg_temp":        avg_temp,
            "avg_precip":      avg_precip,
            "avg_rainy":       avg_rainy,
            "pct_dry":         pct_dry,
            "pct_good_temp":   pct_good_temp,
            "yoy_temp":        yoy_temp_val,
            "yoy_temp_years":  yoy_temp_years,
            "yoy_precip":      yoy_precip_val,
            "yoy_precip_years": yoy_precip_years,
            "year_min":        int(df["year"].min()),
            "year_max":        int(df["year"].max()),
        }

    def export_kpi_metadata(self, kpis: dict):
        """
        Auto-generates analysis_results/kpi_metadata.md from live KPI values.
        Called automatically at the end of run() — no manual editing needed.
        """
        def status(met: bool) -> str:
            return "✅ Met" if met else "❌ Not Met"

        yoy_temp_str = (
            f"{kpis['yoy_temp']:+.2f}% ({kpis['yoy_temp_years'][0]}→{kpis['yoy_temp_years'][1]})"
            if kpis["yoy_temp"] is not None else "N/A"
        )
        yoy_temp_met = abs(kpis["yoy_temp"]) <= 1 if kpis["yoy_temp"] is not None else None
        yoy_temp_status = status(yoy_temp_met) if yoy_temp_met is not None else "⚠️ Insufficient data"

        yoy_precip_str = (
            f"{kpis['yoy_precip']:+.2f}% ({kpis['yoy_precip_years'][0]}→{kpis['yoy_precip_years'][1]})"
            if kpis["yoy_precip"] is not None else "N/A"
        )
        yoy_precip_met = abs(kpis["yoy_precip"]) <= 10 if kpis["yoy_precip"] is not None else None
        yoy_precip_status = status(yoy_precip_met) if yoy_precip_met is not None else "⚠️ Insufficient data"

        generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")

        md = f"""# Pokhara Climate Analytics — KPI Metadata
> Auto-generated by `kpi_analysis.py` on {generated_at}
> Data period: {kpis['year_min']}–{kpis['year_max']} | Source: Pokhara Weather DB

---

## Number KPIs

| Metric | Value | Target | Data Source | Frequency | Status |
|---|---|---|---|---|---|
| Average Temperature | {kpis['avg_temp']} °C | >= 18 °C | `monthly_historical` table | Monthly | {status(kpis['avg_temp'] >= 18)} |
| Avg Monthly Precipitation | {kpis['avg_precip']} mm | <= 300 mm | `monthly_historical` table | Monthly | {status(kpis['avg_precip'] <= 300)} |
| Avg Rainy Days per Month | {kpis['avg_rainy']} days | <= 12 days | `monthly_historical` table | Monthly | {status(kpis['avg_rainy'] <= 12)} |

---

## Progress KPIs

| Metric | Value | Target | Data Source | Frequency | Status |
|---|---|---|---|---|---|
| % Dry Months (< 100 mm precip) | {kpis['pct_dry']}% | >= 40% | `monthly_historical` GROUP BY month | Annual | {status(kpis['pct_dry'] >= 40)} |
| % Comfortable Temp Months (15–28 °C) | {kpis['pct_good_temp']}% | >= 50% | `monthly_historical` GROUP BY month | Annual | {status(kpis['pct_good_temp'] >= 50)} |

---

## Change KPIs

| Metric | Value | Target | Data Source | Frequency | Status |
|---|---|---|---|---|---|
| YoY Temperature Change | {yoy_temp_str} | <= ±1% | `monthly_historical` GROUP BY year | Annual | {yoy_temp_status} |
| YoY Precipitation Change | {yoy_precip_str} | <= ±10% | `monthly_historical` GROUP BY year | Annual | {yoy_precip_status} |

---

## Charts Generated

| File | Analysis Type | Module |
|---|---|---|
| `desc_monthly_temperature.png` | Descriptive — Avg monthly temperature bar chart | `descriptive_analytics.py` |
| `kpi_correlation_heatmap.png` | KPI — Weather variable correlation heatmap | `kpi_analysis.py` |
| `pred_forecast_vs_baseline.png` | Predictive — API forecast vs 15-yr historical baseline | `predictive_analysis.py` |
| `pres_tourism_score_bar.png` | Prescriptive — Tourism suitability score by month | `prescriptive_analysis.py` |

---
*All files saved to `analysis_results/` folder.*
"""
        AnalysisExporter.save_markdown(md, "kpi_metadata.md")

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
        AnalysisExporter.save_image(fig, "kpi_correlation_heatmap.png")
        plt.show()
        return fig

    def run(self):
        print("\n>>> Running KPI Analysis...")
        df = self.load_historical()

        if df.empty:
            print("No historical data found.")
            return

        kpis = self.compute_and_print_kpis(df)
        self.plot_correlation_heatmap(df)
        self.export_kpi_metadata(kpis)
        print(">>> KPI Analysis complete.\n")
        return df