
from analytics.descriptive_analytics import DescriptiveAnalytics
from analytics.predictive_analysis import PredictiveAnalytics
from analytics.prescriptive_analysis import PrescriptiveAnalytics
from analytics.kpi_analysis import KPIAnalytics


class DataAnalyser:
    def __init__(self, db_helper):
        self.db_helper = db_helper

    def run_descriptive_analysis(self):
        da = DescriptiveAnalytics(self.db_helper)
        da.run()
    
    def run_predictive_analysis(self):
        pa = PredictiveAnalytics(self.db_helper)
        pa.run()
 
    def run_prescriptive_analysis(self):
        pra = PrescriptiveAnalytics(self.db_helper)
        pra.run()
    
    def run_kpi_analysis(self):
        kpi = KPIAnalytics(self.db_helper)
        kpi.run()

