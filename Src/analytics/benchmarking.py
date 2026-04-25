import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from analytics.analysis_exporter import AnalysisExporter

# ---------------------------------------------------------------------------
# Reference climate data — sourced from publicly available records
# Kathmandu : weather-atlas.com  (long-run monthly averages)
# Interlaken : climate-data.org  (1991–2021 normals)
# ---------------------------------------------------------------------------

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

REFERENCE_CITIES = {
    "Kathmandu": {
        "source": "weather-atlas.com",
        "avg_temp_c":   [10.0, 12.0, 16.0, 20.0, 23.0, 26.0, 25.0, 25.0, 23.0, 19.0, 14.0, 10.0],
        "precip_mm":    [15.0, 20.0, 35.0, 58.0, 122.0, 246.0, 363.0, 331.0, 183.0, 38.0, 8.0, 7.0],
        "rainy_days":   [2,    3,    5,    8,    13,    18,    23,    21,    16,    6,    1,   1  ],
        "humidity_pct": [72,   68,   58,   53,   61,    75,    83,    84,    82,    77,   85,  78 ],
    },
    "Interlaken": {
        "source": "climate-data.org (1991-2021 normals)",
        "avg_temp_c":   [-4.5, -3.5, 0.5,  5.5,  10.5, 14.0, 14.8, 14.5, 11.0, 6.5,  1.5, -3.0],
        "precip_mm":    [109,  109,  129,  114,   138,  165,  222,  200,  148,  100,  116, 118 ],
        "rainy_days":   [12,   12,   13,   10,    13,   14,   19,   17,   13,   11,   13,  13  ],
        "humidity_pct": [80,   76,   78,   80,    78,   79,   81,   81,   82,   82,   82,  81  ],
    },
}

CITY_STYLES = {
    "Pokhara":    {"color": "#D0021B", "marker": "o"},
    "Kathmandu":  {"color": "#4A90D9", "marker": "s"},
    "Interlaken": {"color": "#7ED321", "marker": "^"},
}

# Scoring weights for trekking tourism suitability (must sum to 100)
SCORING_RULES = {
    "avg_temp_c":   {"weight": 25, "ideal_low": 15, "ideal_high": 28, "direction": "range"},
    "precip_mm":    {"weight": 30, "direction": "lower_is_better"},
    "rainy_days":   {"weight": 25, "direction": "lower_is_better"},
    "humidity_pct": {"weight": 20, "direction": "lower_is_better"},
}


class BenchmarkingAnalytics:

    def __init__(self, db_helper):
        self.db = db_helper

    # ------------------------------------------------------------------ #
    #  Data Loading                                                        #
    # ------------------------------------------------------------------ #
    def load_pokhara_monthly(self):
        cursor = self.db.mydb.cursor(dictionary=True)
        cursor.execute("""
            SELECT
                month,
                AVG(avg_temp_c)       AS avg_temp_c,
                AVG(total_precip_mm)  AS precip_mm,
                AVG(rainy_days)       AS rainy_days,
                AVG(avg_humidity_pct) AS humidity_pct
            FROM monthly_historical
            GROUP BY month
            ORDER BY month
        """)
        rows = cursor.fetchall()
        cursor.close()
        df = pd.DataFrame(rows)
        for col in ["avg_temp_c", "precip_mm", "rainy_days", "humidity_pct"]:
            df[col] = df[col].astype(float)
        return df

    def _build_comparison_df(self, pokhara_df):
        records = []
        for i, month in enumerate(MONTHS):
            m = i + 1
            records.append({
                "city": "Pokhara", "month": month, "month_num": m,
                "avg_temp_c":   float(pokhara_df.loc[pokhara_df["month"] == m, "avg_temp_c"].values[0]),
                "precip_mm":    float(pokhara_df.loc[pokhara_df["month"] == m, "precip_mm"].values[0]),
                "rainy_days":   float(pokhara_df.loc[pokhara_df["month"] == m, "rainy_days"].values[0]),
                "humidity_pct": float(pokhara_df.loc[pokhara_df["month"] == m, "humidity_pct"].values[0]),
            })
            for city, data in REFERENCE_CITIES.items():
                records.append({
                    "city": city, "month": month, "month_num": m,
                    "avg_temp_c":   data["avg_temp_c"][i],
                    "precip_mm":    data["precip_mm"][i],
                    "rainy_days":   data["rainy_days"][i],
                    "humidity_pct": data["humidity_pct"][i],
                })
        return pd.DataFrame(records)

    # ------------------------------------------------------------------ #
    #  Dynamic Scoring Engine                                              #
    # ------------------------------------------------------------------ #
    def _compute_summary(self, df):
        """Annual averages per city + derived metrics."""
        summary = df.groupby("city").agg(
            avg_temp_c   = ("avg_temp_c",   "mean"),
            precip_mm    = ("precip_mm",    "mean"),
            rainy_days   = ("rainy_days",   "mean"),
            humidity_pct = ("humidity_pct", "mean"),
        ).round(1)

        for city in summary.index:
            sub = df[df["city"] == city]
            summary.loc[city, "dry_months"]         = int((sub["precip_mm"] < 100).sum())
            summary.loc[city, "comfortable_months"]  = int(sub["avg_temp_c"].between(15, 28).sum())

        return summary

    def _score_city(self, row, all_values):
        """Score 0-100 for trekking tourism; each metric scored relative to the field."""
        score = 0
        for metric, rule in SCORING_RULES.items():
            w   = rule["weight"]
            val = row[metric]

            if rule["direction"] == "range":
                low, high = rule["ideal_low"], rule["ideal_high"]
                if low <= val <= high:
                    score += w
                else:
                    gap    = min(abs(val - low), abs(val - high))
                    score += max(0, w - gap * 1.5)

            elif rule["direction"] == "lower_is_better":
                vals  = all_values[metric]
                worst = max(vals)
                best  = min(vals)
                score += w if worst == best else w * (worst - val) / (worst - best)

        return round(score, 1)

    def _compute_scores(self, summary):
        """Score and rank all cities — returns summary sorted by rank."""
        all_values = {m: summary[m].tolist() for m in SCORING_RULES}
        scores     = {city: self._score_city(row, all_values) for city, row in summary.iterrows()}
        summary["score"] = pd.Series(scores)
        summary["rank"]  = summary["score"].rank(ascending=False).astype(int)
        return summary.sort_values("rank")

    def _winner(self, summary, metric, lower_is_better=False):
        return summary[metric].idxmin() if lower_is_better else summary[metric].idxmax()

    def _verdict(self, score):
        if score >= 75:   return "Excellent — highly recommended for trekking tourism"
        elif score >= 55: return "Good — recommended with seasonal awareness"
        elif score >= 35: return "Moderate — acceptable in specific months only"
        else:             return "Poor — not recommended for general trekking tourism"

    # ------------------------------------------------------------------ #
    #  One Consolidated Chart                                              #
    # ------------------------------------------------------------------ #
    def plot_comparison(self, df, summary):
        cities = summary.index.tolist()  # ordered by rank
        x      = np.arange(len(MONTHS))
        width  = 0.28

        fig, axes = plt.subplots(3, 1, figsize=(14, 13), sharex=True)
        fig.suptitle(
            "Climate Benchmarking — " + " vs ".join(cities),
            fontsize=15, fontweight="bold", y=0.98
        )

        # Subplot 1: Temperature (line)
        ax1 = axes[0]
        for city in cities:
            sub = df[df["city"] == city].sort_values("month_num")
            ax1.plot(x, sub["avg_temp_c"].values,
                     color=CITY_STYLES[city]["color"], marker=CITY_STYLES[city]["marker"],
                     linewidth=2, markersize=5,
                     label=f"{city} (#{summary.loc[city,'rank']})")
        ax1.axhline(15, color="gray", linewidth=0.8, linestyle="--", alpha=0.5, label="15 C comfort floor")
        ax1.axhline(28, color="gray", linewidth=0.8, linestyle="-.", alpha=0.5, label="28 C comfort ceiling")
        ax1.set_ylabel("Avg Temp (C)")
        ax1.set_title("Average Monthly Temperature", fontsize=11)
        ax1.legend(fontsize=8, loc="upper left")
        ax1.grid(axis="y", linestyle="--", alpha=0.3)

        # Subplot 2: Precipitation (grouped bar)
        ax2 = axes[1]
        for i, city in enumerate(cities):
            sub = df[df["city"] == city].sort_values("month_num")
            ax2.bar(x + (i - 1) * width, sub["precip_mm"].values,
                    width=width, color=CITY_STYLES[city]["color"],
                    label=f"{city} (#{summary.loc[city,'rank']})", alpha=0.85, edgecolor="white")
        ax2.axhline(300, color="#F5A623", linewidth=1.2, linestyle="--", alpha=0.7, label="300mm caution")
        ax2.set_ylabel("Precipitation (mm)")
        ax2.set_title("Monthly Precipitation", fontsize=11)
        ax2.legend(fontsize=8, loc="upper left")
        ax2.grid(axis="y", linestyle="--", alpha=0.3)

        # Subplot 3: Rainy days (grouped bar)
        ax3 = axes[2]
        for i, city in enumerate(cities):
            sub = df[df["city"] == city].sort_values("month_num")
            ax3.bar(x + (i - 1) * width, sub["rainy_days"].values,
                    width=width, color=CITY_STYLES[city]["color"],
                    label=f"{city} (#{summary.loc[city,'rank']})", alpha=0.85, edgecolor="white")
        ax3.set_ylabel("Rainy Days")
        ax3.set_title("Rainy Days per Month", fontsize=11)
        ax3.legend(fontsize=8, loc="upper left")
        ax3.grid(axis="y", linestyle="--", alpha=0.3)
        ax3.set_xticks(x)
        ax3.set_xticklabels(MONTHS)

        plt.tight_layout()
        chart_filename = "bench_city_comparison.png"
        AnalysisExporter.save_image(fig, chart_filename)
        plt.show()
        return fig, chart_filename

    # ------------------------------------------------------------------ #
    #  Dynamic Markdown Report                                             #
    # ------------------------------------------------------------------ #
    def export_benchmarking_report(self, summary, chart_filename):
        generated = datetime.now().strftime("%Y-%m-%d %H:%M")
        cities    = summary.index.tolist()   # sorted by rank
        winner    = cities[0]
        loser     = cities[-1]

        # --- Data source table ---
        source_rows = "| **Pokhara** | `monthly_historical` database table (15-year averages) |\n"
        for city, data in REFERENCE_CITIES.items():
            source_rows += f"| **{city}** | {data['source']} |\n"

        # --- Ranked summary table (sorted by score, winner first) ---
        rank_rows = ""
        for city in cities:
            r   = summary.loc[city]
            rank_rows += (
                f"| #{int(r['rank'])} | **{city}** | {r['avg_temp_c']} | "
                f"{r['precip_mm']} | {r['rainy_days']} | {r['humidity_pct']} | "
                f"{int(r['dry_months'])}/12 | {int(r['comfortable_months'])}/12 | "
                f"**{r['score']}** |\n"
            )

        # --- Metric winners (all computed from data) ---
        warmest    = self._winner(summary, "avg_temp_c")
        driest     = self._winner(summary, "precip_mm",    lower_is_better=True)
        fewest_rain= self._winner(summary, "rainy_days",   lower_is_better=True)
        most_comf  = self._winner(summary, "comfortable_months")
        most_dry   = self._winner(summary, "dry_months")

        # --- Dynamic temperature insight ---
        temp_comparisons = []
        for city in cities:
            if city == winner:
                continue
            diff = round(summary.loc[winner, "avg_temp_c"] - summary.loc[city, "avg_temp_c"], 1)
            direction = "warmer" if diff > 0 else "cooler"
            temp_comparisons.append(f"**{abs(diff)}°C {direction} than {city}**")
        temp_line = f"{warmest} is the warmest city — " + " and ".join(temp_comparisons) + "."

        # --- Dynamic comfort insight ---
        comf_parts = [
            f"{c}: **{int(summary.loc[c,'comfortable_months'])}/12 months**"
            for c in summary.sort_values("comfortable_months", ascending=False).index
        ]
        comf_line = "Comfortable temperature window (15–28°C): " + " | ".join(comf_parts) + "."

        # --- Dynamic precipitation insight ---
        precip_parts = [
            f"{c}: **{summary.loc[c,'precip_mm']} mm/month**"
            for c in summary.sort_values("precip_mm").index
        ]
        precip_line = "Ranked driest to wettest — " + " | ".join(precip_parts) + "."

        # --- Dynamic dry months insight ---
        dry_parts = [
            f"{c}: **{int(summary.loc[c,'dry_months'])}/12**"
            for c in summary.sort_values("dry_months", ascending=False).index
        ]
        dry_line = "Dry months (< 100mm): " + " | ".join(dry_parts) + "."

        # --- Verdict per city ---
        verdict_rows = ""
        for city in cities:
            s = summary.loc[city, "score"]
            verdict_rows += f"- **{city}** (score {s}/100): {self._verdict(s)}\n"

        # --- Strategic takeaway (fully computed) ---
        best_dry  = int(summary.loc[winner, "dry_months"])
        best_comf = int(summary.loc[winner, "comfortable_months"])
        takeaway  = (
            f"**{winner}** ranks #1 with a score of **{summary.loc[winner,'score']}/100**. "
            f"With {best_dry} dry months and {best_comf} comfortable-temperature months per year, "
            f"it offers the strongest climate window for trekking tourism. "
            f"{loser} ranks last ({summary.loc[loser,'score']}/100) and is the least suitable "
            f"for year-round outdoor tourism based on these metrics."
        )

        md = f"""# Climate Benchmarking Report
> Auto-generated by `benchmarking.py` on {generated}
> Pokhara data: `monthly_historical` DB | Reference cities: publicly available climate records

---

## Cities Compared

| City | Data Source |
|---|---|
{source_rows}
---

## Visualisation

![City Comparison Chart](bench_city_comparison.png)

> Saved to `analysis_results/{chart_filename}`

---

## Ranked Summary

*Sorted by trekking tourism suitability score (0-100).*
*Score weights: precipitation 30% | temperature 25% | rainy days 25% | humidity 20%.*

| Rank | City | Avg Temp (C) | Precip (mm/mo) | Rainy Days/mo | Humidity (%) | Dry Months | Comf. Months | Score |
|---|---|---|---|---|---|---|---|---|
{rank_rows}
---

## Key Insights

**Temperature:** {temp_line}
{comf_line}

**Precipitation:** {precip_line}
{dry_line}

**Rainy Days:** {fewest_rain} has the fewest rainy days ({summary.loc[fewest_rain, 'rainy_days']} days/month avg), giving the most reliable outdoor-activity window.

---

## Verdict

{verdict_rows}
**Overall:** {takeaway}

---
*Re-run `benchmarking.py` to refresh all values from the latest DB data.*
"""
        AnalysisExporter.save_markdown(md, "benchmarking_report.md")

    # ------------------------------------------------------------------ #
    #  Print Insights                                                      #
    # ------------------------------------------------------------------ #
    def print_insights(self, summary):
        print("\n===== BENCHMARKING INSIGHTS =====")
        print(f"\n  {'Rank':<6} {'City':<12} {'Temp':>8} {'Precip':>10} {'RainyDays':>11} {'Score':>8}")
        print("  " + "-" * 60)
        for city in summary.index:
            r = summary.loc[city]
            print(f"  #{int(r['rank']):<5} {city:<12} {r['avg_temp_c']:>7}C "
                  f"{r['precip_mm']:>9}mm {r['rainy_days']:>10} days {r['score']:>7}/100")
        winner = summary.index[0]
        loser  = summary.index[-1]
        print(f"\n  -> Best overall  : {winner} ({summary.loc[winner,'score']}/100)")
        print(f"  -> Least suitable: {loser} ({summary.loc[loser,'score']}/100)")
        print("=================================\n")

    # ------------------------------------------------------------------ #
    #  Run                                                                 #
    # ------------------------------------------------------------------ #
    def run(self):
        print("\n>>> Running Benchmarking Analysis...")
        pokhara_df = self.load_pokhara_monthly()

        if pokhara_df.empty:
            print("No Pokhara historical data found.")
            return

        df      = self._build_comparison_df(pokhara_df)
        summary = self._compute_summary(df)
        summary = self._compute_scores(summary)

        fig, chart_filename = self.plot_comparison(df, summary)
        self.print_insights(summary)
        self.export_benchmarking_report(summary, chart_filename)

        print(">>> Benchmarking Analysis complete.\n")
        return df