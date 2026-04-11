import calendar as cal

import pandas as pd
import docx2txt
import re
import os

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
            print("Detected Columns:", df.columns.tolist())
            for _, row in df.iterrows():
                print(f"Processing row: {row.to_dict()}")
                # Here you would typically call a method to insert this data into the database
                # For example: db_helper.insert_season(row['Season'], row['Month Start'], row['Month End'], row['Tourism Level'], row['Avg Temp'])  
                
                months_range = row['Months'].split('–')
                month_start = DateConverter.to_number(months_range[0].strip())
                month_end = DateConverter.to_number(months_range[1].strip())
                print(f"Converted Months: {months_range[0].strip()} -> {month_start}, {months_range[1].strip()} -> {month_end}")
                
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
            print("Extracted Text:", full_text[:500])  # Print the first 500
            
            seasons = ["Winter", "Pre-Monsoon", "Monsoon", "Post-Monsoon"]
            
            for i, seasons in enumerate(seasons):
                next_target = seasons[i + 1] if i + 1 < len(seasons) else '$'
                pattern = rf"{seasons}(.*?){next_target}"
                
                match = re.search(pattern, full_text, re.I)
                
                if match:
                    # clean up text
                    raw_text = match.group(1).strip()
                    
                    clean_text = re.sub(r'^\W+|\W+$', '', raw_text)
                    print(f"Extracted text for {seasons} season: {clean_text[:200]}")  # Print the first 200 characters
                else:
                    print(f"Season '{seasons}' not found in the document.")
        except Exception as e:
            print(f"Error reading Word file '{file_name}': {e}")    