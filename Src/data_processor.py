import calendar as cal

import pandas as pd
import docx2txt
import os
from doc_processor import DocProcessor

class DateConverter:
    @staticmethod
    def to_number(month_name):
        # Ensure the input is handled as a string
        name = str(month_name).strip().capitalize()[:3]
        # Use the alias 'cal' here
        mapping = {month: i for i, month in enumerate(cal.month_abbr) if month}
        return mapping.get(name)

    @staticmethod
    def to_full_name(month_num):
        """Converts 1-12 back to 'January', 'February', etc."""
        try:
            return cal.month_name[int(month_num)]
        except (ValueError, IndexError):
            return "Invalid Month"
    

print(DateConverter.to_number("Jan"))


class WeatherDataProcessor:
    def __init__(self, db_helper):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.base_path = os.path.join(base_dir, "..", "resources")
        self.db_helper = db_helper
    
    # Process Excel file to extract season information and save to database
    def process_excel_seasonal_data(self, file_name):
        file_path = os.path.join(self.base_path, file_name)
        print(f"Processing Excel file: {file_path}")
        
        try:
            
            df = pd.read_excel(file_path, sheet_name="Seasonal Summary", skiprows=3)
            print(f"Excel file '{file_name}' read successfully.")
            
            print("Iterating through rows to insert season data into database...")
            for _, row in df.iterrows():
                months_range = row['Months'].split('–')
                month_start = DateConverter.to_number(months_range[0].strip())
                month_end = DateConverter.to_number(months_range[1].strip())
                
                success = self.db_helper.insert_season(
                    name=row['Season'],
                    start=month_start,
                    end=month_end,
                    tourism=row['Tourism Level'],
                    temp=row['Avg Temp (°C)'],
                    precip=row['Avg Monthly Precip (mm)'], # Fixed name
                    humidity=row['Avg Humidity (%)'],
                    cloud=row['Cloud Cover (%)'],
                    rainy_days=row['Rainy Days/Month'],
                    features=row['Key Weather Features']
                    )
                
                if success:
                    print(f"Inserted season '{row['Season']}' into database successfully.")
                else:
                    print(f"Failed to insert season '{row['Season']}' into database.")
            print("Excel file processing completed.")
            
            print("Data from Excel file stored in the database successfully.")
            
            return df
        except Exception as e:
            print(f"Error reading Excel file '{file_name}': {e}")
            return None
    
    
    # Process Word document to extract season information and save to database
    def process_docx(self, file_name):
        file_path = os.path.join(self.base_path, file_name)
        print(f"Processing Word file: {file_path}")
        
        try:
            full_text = docx2txt.process(file_path)
            print(f"Word file '{file_name}' read successfully.")
            
            print("Starting season extraction...")
            doc_processor = DocProcessor(full_text)
            seasons_data = doc_processor.extract_season_info()
            print("Season Data Extraction Completed")
            
            print("Saving season data to database...")
            result = doc_processor.save_season_data(self.db_helper, seasons_data)
            
            if result:
                print("All season data saved to database successfully.")
                print("Process Word File completed.")
            else:
                print("Failed to save some or all season data to database.")
        
        except Exception as e:
            print(f"Error reading Word file '{file_name}': {e}")
    
    def process_csv(self, file_name):
        file_path = os.path.join(self.base_path, file_name)
        print(f"Processing CSV file: {file_path}")
        
        try:
            print(f"Reading CSV file '{file_name}'...")
            df = pd.read_csv(file_path)
            if df.empty:
                print(f"CSV file '{file_name}' is empty.")
            else:
                success_count = 0
                failed_count = 0
                for _, row in df.iterrows():
                    season = self.db_helper.get_season_by_month(int(row["month"]))
                    success = self.db_helper.insert_monthly_record(
                        season_id=season['season_id'] if season else None,
                        year=int(row["year"]),
                        month=int(row["month"]),
                        month_name=row["month_name"],
                        avg_temp_c=float(row["avg_temp_c"]),
                        max_temp_c=float(row["max_temp_c"]),
                        min_temp_c=float(row["min_temp_c"]),
                        total_precip_mm=float(row["total_precip_mm"]),
                        avg_humidity_pct=int(row["avg_humidity_pct"]),
                        avg_wind_spd_ms=float(row["avg_wind_spd_ms"]),
                        avg_cloud_cover_pct=int(row["avg_cloud_cover_pct"]),
                        rainy_days=int(row["rainy_days"]),
                        season=row["season"]
                    )
                    if success:
                        success_count += 1
                    else:
                        failed_count += 1
                print(f"CSV file '{file_name}' processed successfully. {success_count} records inserted, {failed_count} records failed.")
            return df
        except Exception as e:
            print(f"Error reading CSV file '{file_name}': {e}")
            return None
    
    def process_excel_climate_baseline(self, file_name):
        file_path = os.path.join(self.base_path, file_name)
        print(f"Processing Excel file for climate baseline: {file_path}")
        
        try:
            
            df = pd.read_excel(file_path, sheet_name="Monthly Averages", skiprows=3)
            print(f"Excel file '{file_name}' read successfully.")
            
            success_count = 0
            failed_count = 0
            
            for _, row in df.iterrows():
                month_num = DateConverter.to_number(str(row['Month']))
                
                success = self.db_helper.insert_climate_baseline(
                    month=month_num,
                    month_name=str(row['Month']),
                    normal_avg_temp_c=float(row['Avg Temp (°C)']),
                    normal_max_temp_c=float(row['Max Temp (°C)']),
                    normal_min_temp_c=float(row['Min Temp (°C)']),
                    normal_precip_mm=float(row['Total Precip (mm)']),
                    normal_humidity_pct=int(row['Humidity (%)']),
                    normal_wind_ms=float(row['Wind Speed (m/s)']),
                    normal_cloud_cover_pct=int(row['Cloud Cover (%)']),
                    normal_rainy_days=int(row['Rainy Days'])
                )
                
                if(success):
                    success_count += 1
                else:
                    failed_count += 1
                    
            print(f"Excel file '{file_name}' processed successfully. {success_count} records inserted, {failed_count} records failed.")
            return df
        except Exception as e:
            print(f"Error reading Excel file '{file_name}': {e}")
            return None
    
    def process_api(self, api_client):
        print("Fetching forecast data from API...")
        try:
            raw_data = api_client.get_current_forecast()
            if not raw_data:
                print("No data returned from API.")
                return None

            print("Parsing API data...")
            records = api_client.parse_forecast(raw_data)

            success_count = 0
            failed_count = 0

            print("Inserting API data into database...")
            for record in records:
                success = self.db_helper.insert_daily_forecast(
                    forecast_date=          record["forecast_date"],
                    year=                   record["year"],
                    month=                  record["month"],
                    month_name=             record["month_name"],
                    avg_temp_c=             record["avg_temp_c"],
                    max_temp_c=             record["max_temp_c"],
                    min_temp_c=             record["min_temp_c"],
                    precip_mm=              record["precip_mm"],
                    precip_probability_pct= record["precip_probability_pct"],
                    humidity_pct=           record["humidity_pct"],
                    wind_speed_ms=          record["wind_speed_ms"],
                    wind_gust_ms=           record["wind_gust_ms"],
                    wind_direction=         record["wind_direction"],
                    cloud_cover_pct=        record["cloud_cover_pct"],
                    visibility_km=          record["visibility_km"],
                    uv_index=               record["uv_index"],
                    dewpoint_c=             record["dewpoint_c"],
                    pressure_hpa=           record["pressure_hpa"],
                    weather_description=    record["weather_description"],
                    data_source=            record["data_source"]
                )
                if success:
                    success_count += 1
                else:
                    failed_count += 1

            print(f"API processing completed. {success_count} inserted, {failed_count} failed.")
            return records

        except Exception as e:
            print(f"Error processing API data: {e}")
            return None