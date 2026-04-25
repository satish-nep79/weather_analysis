import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from analytics.descriptive_analytics import DescriptiveAnalytics


class DataAnalyser:
    def __init___(self, db_helper):
        self.db_helper = db_helper
    
    # Save Analaysis Charts to a folder with date-based organization
    def save_analysis_image(fig, filename="seasonal_plot.png"):
        base_folder = "analysis_image"
        current_date = datetime.now().strftime("%Y-%m-%d") 
        target_path = os.path.join(base_folder, current_date)
        os.makedirs(target_path, exist_ok=True)
        full_save_path = os.path.join(target_path, filename)
        fig.savefig(full_save_path)
        print(f"Image successfully saved to: {full_save_path}")
    
    def run_descriptive_analysis(self):
        da = DescriptiveAnalytics(self.db_helper)
        df = da.load_data()
        seasonal_summary = da.summary_statistics(df)
        da.plot_monthly_temperature(df)
        da.plot_seasonal_comparison(seasonal_summary)
    

