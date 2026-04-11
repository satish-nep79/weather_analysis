import docx2txt
import re
import json

class DocProcessor:
    def __init__(self, document_text):
        self.document_text = document_text
        # Mapping of season keywords to standardized season names
        self.season_map  = {
        "Winter":       "Winter",
        "Pre-Monsoon":  "Pre-Monsoon",
        "Monsoon":      "Monsoon",
        "Post-Monsoon": "Post-Monsoon"
    }
        
    # Detect season headings like "2.1 Winter (December – February)"
    def detect_season(self, line):
        for keyword in self.season_map:
            if re.match(rf'^\d+\.\d+\s+{keyword}', line, re.IGNORECASE):
                return self.season_map[keyword]
        return None
    
    # Extract season information based on detected headings and content structure
    def extract_season_info(self):    
        # Data structure to hold extracted season information
        seasons_data = {}
        current_season = None
        mode = None
        description_lines = []
        bullet_lines = []
        
        try:
            # Split the document into lines and clean them
            lines = [line.strip() for line in self.document_text.splitlines() if line.strip()]
            
            # Loop through lines to detect seasons and extract relevant information
            for line in lines:
                if not line:
                    continue
                
                # Check for season heading
                season = self.detect_season(line)
                
                # Save data for the previous season before starting a new one
                if season:
                    if current_season:
                        seasons_data[current_season] = {
                            "climate_description": self._build_description(description_lines),
                            "season_highlights": self._build_highlights(bullet_lines)
                            }
                    current_season = season
                    mode = "description"
                    description_lines = []
                    bullet_lines = []
                    continue
                
                # Stop processing if we reach the next major section (e.g., "3. Weather Analysis")
                if current_season and re.match(r'^3\.', line):
                    break
                
                # Save lines based on the current mode (description or bullet points)
                if current_season:
                    if re.match(r'^key characteristics', line, re.IGNORECASE):
                        mode = "bullets"
                        continue
                    
                    if mode == "description":
                        description_lines.append(line)
                    elif mode == "bullets": 
                        bullet_lines.append(line)
            
            # Save season data from the last detected season
            if current_season and current_season not in seasons_data:
                seasons_data[current_season] = {
                    "climate_description": self._build_description(description_lines),
                    "season_highlights":   self._build_highlights(bullet_lines)
                }

            return seasons_data
                                
        except Exception as e:
            print(f"Error processing document: {e}")
            return None
    
    # Method to save extracted season data into the database using DBHelper
    def save_season_data(self, db_helper, seasons_data):
        try:
            for season_name, data in seasons_data.items():
                climate_description = data.get("climate_description", "")
                season_highlights = data.get("season_highlights", [])
                success = db_helper.update_season_description(season_name, climate_description, season_highlights)
                if success:
                    print(f"Updated season '{season_name}' with description and highlights successfully.")
                else:
                    print(f"Failed to update season '{season_name}' with description and highlights.")
            return True
        except Exception as e:
            print(f"Error saving season data to database: {e}")
            return False

    # Helper methods to clean and format text for descriptions
    @staticmethod
    def _build_description(lines):
        full = ' '.join(lines)
        full = re.sub(r'\s+', ' ', full).strip()
        sentences = re.split(r'(?<=[.!?])\s+', full)
        return ' '.join(sentences[:3])

    # Helper method to clean bullet points and join them
    @staticmethod
    def _build_highlights(lines):
        cleaned = []
        for line in lines:
            line = re.sub(r'\s+', ' ', line).strip()
            line = line.replace('\u2014', '-').replace('\u2013', '-')
            if line:
                cleaned.append(line)
        return cleaned
        
        
    