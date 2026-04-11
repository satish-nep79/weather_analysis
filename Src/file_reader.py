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


class WeatherFileReader:
    def __init__(self, db_helper):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.base_path = os.path.join(base_dir, "..", "resources")
        self.db_helper = db_helper
    
    def process_excel_baseline(self, file_name):
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