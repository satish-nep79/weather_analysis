import os

class ChartSaver:
    @staticmethod
    def save_analysis_image(fig, filename="seasonal_plot.png"):
        base_folder = "analysis_image"
        os.makedirs(base_folder, exist_ok=True)
        full_save_path = os.path.join(base_folder, filename)
        fig.savefig(full_save_path)
        print(f"Image successfully saved to: {full_save_path}")