import os
import pandas as pd
from dotenv import load_dotenv
from db_helper import DBHelper

# ---------------------------------------------------------------------------
# Exports all relevant DB tables as CSVs for Power BI / Fabric import.
# Output folder: exports/powerbi/
# Run standalone: python export_for_powerbi.py
# ---------------------------------------------------------------------------

OUTPUT_FOLDER = os.path.join("exports", "csv_powerbi")


def ensure_folder():
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def save_csv(df, filename):
    path = os.path.join(OUTPUT_FOLDER, filename)
    df.to_csv(path, index=False)
    print(f"  Saved: {path}  ({len(df)} rows)")


def export_seasons(db):
    print("\n[1/4] Exporting seasons...")
    cursor = db.mydb.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            season_id,
            season_name,
            month_start,
            month_end,
            tourism_level,
            avg_temp_c,
            avg_precip_mm,
            avg_humidity_pct,
            avg_cloud_cover_pct,
            rainy_days_per_month,
            key_features,
            climate_description
        FROM seasons
        ORDER BY month_start
    """)
    rows = cursor.fetchall()
    cursor.close()
    save_csv(pd.DataFrame(rows), "seasons.csv")


def export_monthly_historical(db):
    print("\n[2/4] Exporting monthly_historical...")
    cursor = db.mydb.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            mh.record_id,
            mh.season_id,
            mh.year,
            mh.month,
            mh.month_name,
            s.season_name,
            mh.avg_temp_c,
            mh.max_temp_c,
            mh.min_temp_c,
            mh.total_precip_mm,
            mh.avg_humidity_pct,
            mh.avg_wind_spd_ms,
            mh.avg_cloud_cover_pct,
            mh.rainy_days
        FROM monthly_historical mh
        LEFT JOIN seasons s ON mh.season_id = s.season_id
        ORDER BY mh.year, mh.month
    """)
    rows = cursor.fetchall()
    cursor.close()
    df = pd.DataFrame(rows)

    # Derived columns — useful for Power BI slicers and conditional formatting
    df["date"]           = pd.to_datetime(df[["year", "month"]].assign(day=1))
    df["temp_range_c"]   = (df["max_temp_c"] - df["min_temp_c"]).round(1)
    df["is_dry_month"]   = (df["total_precip_mm"] < 100).astype(int)
    df["comfort_window"] = df["avg_temp_c"].between(15, 28).astype(int)

    save_csv(df, "monthly_historical.csv")


def export_daily_forecast(db):
    print("\n[3/4] Exporting daily_forecast...")
    cursor = db.mydb.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            forecast_id,
            season_id,
            forecast_date,
            year,
            month,
            month_name,
            avg_temp_c,
            max_temp_c,
            min_temp_c,
            precip_mm,
            precip_probability_pct,
            humidity_pct,
            wind_speed_ms,
            wind_gust_ms,
            wind_direction,
            cloud_cover_pct,
            visibility_km,
            uv_index,
            dewpoint_c,
            pressure_hpa,
            weather_description,
            data_source
        FROM daily_forecast
        ORDER BY forecast_date
    """)
    rows = cursor.fetchall()
    cursor.close()
    df = pd.DataFrame(rows)

    if not df.empty:
        df["forecast_date"] = pd.to_datetime(df["forecast_date"])
        df["rain_risk"] = pd.cut(
            df["precip_probability_pct"],
            bins=[-1, 39, 69, 100],
            labels=["Low", "Medium", "High"]
        )

    save_csv(df, "daily_forecast.csv")


def export_climate_baseline(db):
    print("\n[4/4] Exporting climate_baseline...")
    cursor = db.mydb.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            baseline_id,
            month,
            month_name,
            normal_avg_temp_c,
            normal_max_temp_c,
            normal_min_temp_c,
            normal_precip_mm,
            normal_humidity_pct,
            normal_wind_ms,
            normal_cloud_cover_pct,
            normal_rainy_days
        FROM climate_baseline
        ORDER BY month
    """)
    rows = cursor.fetchall()
    cursor.close()
    save_csv(pd.DataFrame(rows), "climate_baseline.csv")


def print_summary():
    print("\n" + "=" * 55)
    print("  Power BI Export Complete")
    print(f"  All CSVs saved to: {os.path.abspath(OUTPUT_FOLDER)}")
    print("=" * 55)
    print("\n  Import order in Power BI / Fabric:")
    print("  1. seasons.csv              (dimension table)")
    print("  2. climate_baseline.csv     (dimension table)")
    print("  3. monthly_historical.csv   (main fact table)")
    print("  4. daily_forecast.csv       (fact table)")
    print("\n  Relationships to create in Model view:")
    print("  seasons[season_id]       -> monthly_historical[season_id]  (1-to-many)")
    print("  climate_baseline[month]  -> monthly_historical[month]      (1-to-many)")
    print("  climate_baseline[month]  -> daily_forecast[month]          (1-to-many)")
    print("=" * 55 + "\n")


def main():
    print("Initializing Power BI export...")
    load_dotenv()

    db = DBHelper(
        os.getenv("DB_HOST"),
        os.getenv("DB_USER"),
        os.getenv("DB_PASSWORD")
    )
    db.prepare_database(os.getenv("DB_NAME"))

    ensure_folder()

    export_seasons(db)
    export_monthly_historical(db)
    export_daily_forecast(db)
    export_climate_baseline(db)

    print_summary()


if __name__ == "__main__":
    main()