import os
from dotenv import load_dotenv
from db_helper import DBHelper
from api_client import WetherAPIClient
from file_reader import WeatherFileReader

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
    print("Database setup completed successfully... ")
    
    #Reading baseline data from Excel file
    print("Processing Data From different sources...")
    file_reader = WeatherFileReader(db_helper)
    file_reader.process_excel_baseline("pokhara_weather_seasonal_analysis.xlsx")
    file_reader.process_docx("pokhara_climate_report.docx")
    
    # Fetching API key from environment variables
    api_key = os.getenv("API_KEY")
    print("API key loaded successfully... ")
    # Creating an instance of WetherAPIClient with the loaded API key
    api_client = WetherAPIClient(api_key)
    # api_client.get_current_forcase()   
    

    
if __name__ == "__main__":
    main()