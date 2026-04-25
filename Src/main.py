import os
from dotenv import load_dotenv
from db_helper import DBHelper
from api_client import WeatherAPIClient
from data_processor import WeatherDataProcessor
from analytics.coordinator import DataAnalyser


def main():
    print("Initializing project...")
    load_dotenv()

    db_helper = DBHelper(os.getenv("DB_HOST"), os.getenv("DB_USER"), os.getenv("DB_PASSWORD"))
    db_helper.prepare_database(os.getenv("DB_NAME"))

    print("Processing data from different sources...")
    data_processor = WeatherDataProcessor(db_helper)
    data_processor.process_excel_seasonal_data("pokhara_weather_seasonal_analysis.xlsx")
    data_processor.process_docx("pokhara_climate_report.docx")
    data_processor.process_csv("pokhara_monthly_weather_historical.csv")
    data_processor.process_excel_climate_baseline("pokhara_weather_seasonal_analysis.xlsx")

    api_client = WeatherAPIClient(os.getenv("API_KEY"))
    data_processor.process_api(api_client)

    analyser = DataAnalyser(db_helper)
    analyser.run_descriptive_analysis()
    analyser.run_predictive_analysis()
    analyser.run_prescriptive_analysis()
    analyser.run_kpi_analysis()


if __name__ == "__main__":
    main()