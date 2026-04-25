import os
from dotenv import load_dotenv
from db_helper import DBHelper
from api_client import WeatherAPIClient
from data_processor import WeatherDataProcessor
from analytics.coordinator import DataAnalyser

def main():
    initializeApp()
    print("Project initialized successfully...")

    

def initializeApp():
    print("Initializing project...")
    print("Loading environment variables...")
    load_dotenv()
    
    # Fetching database credentials from environment variables
    db_host = os.getenv("DB_HOST")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    print("Environment variables loaded successfully... ")
    
    # Creating an instance of DBHelper with the loaded credentials
    print("Setting up database......")
    db_helper = DBHelper(db_host, db_user, db_password)
    db_helper.prepare_database(os.getenv("DB_NAME"))
    # db_helper.delete_database(os.getenv("DB_NAME"))
    print("Database setup completed successfully... ")
    
    #Reading baseline data from Excel file
    print("Processing Data From different sources...")
    data_processor = WeatherDataProcessor(db_helper)
    data_processor.process_excel_seasonal_data("pokhara_weather_seasonal_analysis.xlsx")
    data_processor.process_docx("pokhara_climate_report.docx")
    data_processor.process_csv("pokhara_monthly_weather_historical.csv")
    data_processor.process_excel_climate_baseline("pokhara_weather_seasonal_analysis.xlsx")
    
    # Fetching API key from environment variables
    api_key = os.getenv("API_KEY")
    print("API key loaded successfully... ")
    # Creating an instance of WetherAPIClient with the loaded API key
    api_client = WeatherAPIClient(api_key)
    data_processor.process_api(api_client)
    
    analyser = DataAnalyser(db_helper)
    # analyser.run_descriptive_analysis()
    analyser.run_predictive_analysis()
    analyser.run_prescriptive_analysis()
    analyser.run_kpi_analysis()
    

    
if __name__ == "__main__":
    main()