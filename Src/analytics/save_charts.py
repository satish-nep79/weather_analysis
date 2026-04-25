
import os
from datetime import datetime

class ChartSaver:
    
    
    @staticmethod
    # Save Analaysis Charts to a folder with date-based organization
    def save_analysis_image(fig, filename="seasonal_plot.png"):
        base_folder = "analysis_image"
        current_date = datetime.now().strftime("%Y-%m-%d") 
        target_path = os.path.join(base_folder, current_date)
        os.makedirs(target_path, exist_ok=True)
        full_save_path = os.path.join(target_path, filename)
        fig.savefig(full_save_path)
        print(f"Image successfully saved to: {full_save_path}")