import os
from datetime import datetime


class AnalysisExporter:
    OUTPUT_FOLDER = "analysis_results"

    @staticmethod
    def _ensure_folder():
        os.makedirs(AnalysisExporter.OUTPUT_FOLDER, exist_ok=True)

    @staticmethod
    def save_image(fig, filename="plot.png"):
        AnalysisExporter._ensure_folder()
        path = os.path.join(AnalysisExporter.OUTPUT_FOLDER, filename)
        fig.savefig(path)
        print(f"Image saved: {path}")

    @staticmethod
    def save_markdown(content: str, filename="kpi_metadata.md"):
        AnalysisExporter._ensure_folder()
        path = os.path.join(AnalysisExporter.OUTPUT_FOLDER, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Markdown saved: {path}")