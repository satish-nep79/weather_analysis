import mysql.connector
import json

class DBHelper:
    
    
    def __init__(self, host, user, password):
        # Establishing a connection to the MySQL database using the provided credentials
        print("Connecting to Database...")
        self.mydb = mysql.connector.connect(
            host=host,
            user=user,
            password=password
        )
        print("Database connection established")
        self.mycursor = self.mydb.cursor()
        
        
    # Preparing the database for use:
    # - Creating the database if it does not already exist
    # - Selecting the database for subsequent operations
    # - Executing the necessary SQL commands to set up the database structure (e.g., creating tables)
    # - Handling any exceptions that may occur during the database setup process and providing appropriate feedback
    # This method ensures that the database is ready for use before any further operations are performed.
    def prepare_database(self, database_name):
        print(f"Setting up database '{database_name}'...")
        cursor = self.mydb.cursor()
        try:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")
            cursor.execute(f"USE {database_name}")
            self.initialize_db_schema()
            print(f"Database '{database_name}' is ready for use.")
        except Exception as e:
            print(f"Database setup failed: {e}")
            raise
        finally:
            cursor.close()
            
    def initialize_db_schema(self):
        cursor = self.mydb.cursor()
        
        # SQL commands to create necessary tables and define relationships
        queries = {
            # 1. SEASONS (Independent)
            "seasons": """
            CREATE TABLE IF NOT EXISTS seasons (
                season_id INT AUTO_INCREMENT PRIMARY KEY,
                season_name VARCHAR(20) NOT NULL UNIQUE,
                month_start INT,
                month_end INT,
                tourism_level VARCHAR(20),
                avg_temp_c FLOAT,
                avg_precip_mm FLOAT,
                avg_humidity_pct FLOAT,
                avg_cloud_cover_pct FLOAT,
                rainy_days_per_month INT,
                climate_description TEXT,
                season_highlights TEXT,
                key_features VARCHAR(255)
            ) ENGINE=InnoDB;
            """,

            # 2. CLIMATE BASELINE (Independent - Monthly Norms)
            "climate_baseline": """
            CREATE TABLE IF NOT EXISTS climate_baseline (
                baseline_id INT AUTO_INCREMENT PRIMARY KEY,
                month INT NOT NULL UNIQUE,
                month_name VARCHAR(15),
                normal_avg_temp_c FLOAT,
                normal_max_temp_c FLOAT,
                normal_min_temp_c FLOAT,
                normal_precip_mm FLOAT,
                normal_humidity_pct INT,
                normal_wind_ms FLOAT,
                normal_cloud_cover_pct INT,
                normal_rainy_days INT
            ) ENGINE=InnoDB;
            """,

            # 3. MONTHLY HISTORICAL (Dependent on Seasons)
            "monthly_historical": """
            CREATE TABLE IF NOT EXISTS monthly_historical (
                record_id INT AUTO_INCREMENT PRIMARY KEY,
                season_id INT NULL,
                year INT NOT NULL,
                month INT NOT NULL,
                month_name VARCHAR(15),
                avg_temp_c FLOAT,
                max_temp_c FLOAT,
                min_temp_c FLOAT,
                total_precip_mm FLOAT,
                avg_humidity_pct INT,
                avg_wind_spd_ms FLOAT,
                avg_cloud_cover_pct INT,
                rainy_days INT,
                UNIQUE KEY unique_month_year (year, month),
                FOREIGN KEY (season_id) REFERENCES seasons(season_id) ON DELETE SET NULL
            ) ENGINE=InnoDB;
            """,

            # 4. DAILY FORECAST (Dependent on Seasons)
            "daily_forecast": """
            CREATE TABLE IF NOT EXISTS daily_forecast (
                forecast_id INT AUTO_INCREMENT PRIMARY KEY,
                season_id INT NULL,
                forecast_date DATE NOT NULL UNIQUE,
                year INT,
                month INT,
                month_name VARCHAR(15),
                avg_temp_c FLOAT,
                max_temp_c FLOAT,
                min_temp_c FLOAT,
                precip_mm FLOAT,
                precip_probability_pct INT,
                humidity_pct INT,
                wind_speed_ms FLOAT,
                wind_gust_ms FLOAT,
                wind_direction VARCHAR(10),
                cloud_cover_pct INT,
                visibility_km FLOAT,
                uv_index FLOAT,
                dewpoint_c FLOAT,
                pressure_hpa INT,
                weather_description VARCHAR(255),
                data_source VARCHAR(100),
                FOREIGN KEY (season_id) REFERENCES seasons(season_id) ON DELETE SET NULL
            ) ENGINE=InnoDB;
            """
        }
        
        try:
            print("Checking and initializing database schema...")
            for table_name, command in queries.items():
                cursor.execute(command)
                print(f"Table '{table_name}' is ready.")
            self.mydb.commit()
            print("Database schema secured ... clear")
        except Exception as e:
            print(f"Database schema initialization failed: {e}")
            raise
        finally:
            cursor.close()
            
    
    # Method to insert season data into the 'seasons' table
    def insert_season(self, name, start, end, tourism, temp, precip, humidity, cloud, rainy_days, features):
        cursor = self.mydb.cursor()
        query = """
        INSERT INTO seasons 
        (season_name, month_start, month_end, tourism_level, avg_temp_c, 
        avg_precip_mm, avg_humidity_pct, avg_cloud_cover_pct, rainy_days_per_month, key_features)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            month_start = VALUES(month_start),
            month_end = VALUES(month_end),
            tourism_level = VALUES(tourism_level),
            avg_temp_c = VALUES(avg_temp_c),
            avg_precip_mm = VALUES(avg_precip_mm),
            avg_humidity_pct = VALUES(avg_humidity_pct),
            avg_cloud_cover_pct = VALUES(avg_cloud_cover_pct),
            rainy_days_per_month = VALUES(rainy_days_per_month),
            key_features = VALUES(key_features);
        """
        try:
            # We wrap the variables in a single tuple for the execute command
            values = (name, start, end, tourism, temp, precip, humidity, cloud, rainy_days, features)
            cursor.execute(query, values)
            self.mydb.commit()
            return True
        except Exception as e:
            print(f"DB Insert Error: {e}")
            return False
    
    # Update Method
    # Updates season row with climate description and highlights based on season name
    def update_season_description(self, season_name, climate_description, season_highlights):
        cursor = self.mydb.cursor()
        query = """
            UPDATE seasons
            SET climate_description = %s,
                season_highlights   = %s
            WHERE season_name = %s
        """
        try:
            # Check if season_highlights is a string and convert it to a list if necessary
            if isinstance(season_highlights, str):
                season_highlights = [season_highlights]
            
            # If season_highlights is not a list (e.g., None or other type), set it to an empty list
            if not isinstance(season_highlights, list):
                season_highlights= []    
            
            cursor.execute(query, (climate_description, json.dumps(season_highlights), season_name))
            self.mydb.commit()
            if cursor.rowcount == 0:
                print(f"Warning: '{season_name}' not found — run insert_season first.")
                return False
            print(f"Description updated for: {season_name}")
            return True
        except Exception as e:
            print(f"Failed to update '{season_name}': {e}")
            return False
        finally:
            cursor.close()
    # Method to fetch season information based on month
    def get_season_by_month(self, month):
        cursor = self.mydb.cursor(dictionary=True)
        query = """
            SELECT * FROM seasons
            WHERE
                -- Normal case: start <= end (e.g. Pre-Monsoon: 3 to 5)
                (month_start <= month_end AND %s BETWEEN month_start AND month_end)
                OR
                -- Wrap-around case: start > end (e.g. Winter: 12 to 2)
                (month_start > month_end AND (%s >= month_start OR %s <= month_end))
        """
        try:
            cursor.execute(query, (month, month, month))
            result = cursor.fetchone()
            if not result:
                print(f"No season found for month {month}")
            return result
        except Exception as e:
            print(f"Failed to fetch season for month {month}: {e}")
            return None
        finally:
            cursor.close()
    
    # Method to insert monthly historical data into the 'monthly_historical' table
    def insert_monthly_record(self, season_id, year, month, month_name, avg_temp_c, max_temp_c,
                           min_temp_c, total_precip_mm, avg_humidity_pct,
                           avg_wind_spd_ms, avg_cloud_cover_pct, rainy_days, season):
        cursor = self.mydb.cursor()
        query = """
            INSERT INTO monthly_historical
            (season_id, year, month, month_name, avg_temp_c, max_temp_c, min_temp_c,
            total_precip_mm, avg_humidity_pct, avg_wind_spd_ms,
            avg_cloud_cover_pct, rainy_days)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                season_id           = VALUES(season_id),
                avg_temp_c          = VALUES(avg_temp_c),
                max_temp_c          = VALUES(max_temp_c),
                min_temp_c          = VALUES(min_temp_c),
                total_precip_mm     = VALUES(total_precip_mm),
                avg_humidity_pct    = VALUES(avg_humidity_pct),
                avg_wind_spd_ms     = VALUES(avg_wind_spd_ms),
                avg_cloud_cover_pct = VALUES(avg_cloud_cover_pct),
                rainy_days          = VALUES(rainy_days);
        """
        try:
            values = (season_id, year, month, month_name, avg_temp_c, max_temp_c, min_temp_c,
                    total_precip_mm, avg_humidity_pct, avg_wind_spd_ms,
                    avg_cloud_cover_pct, rainy_days)
            cursor.execute(query, values)
            self.mydb.commit()
            return True
        except Exception as e:
            print(f"Insert error ({year}-{month}): {e}")
            return False
        finally:
            cursor.close()
            
    def insert_climate_baseline(self, month, month_name, normal_avg_temp_c, normal_max_temp_c,
                             normal_min_temp_c, normal_precip_mm, normal_humidity_pct,
                             normal_wind_ms, normal_cloud_cover_pct, normal_rainy_days):
        cursor = self.mydb.cursor()
        query = """
            INSERT INTO climate_baseline
            (month, month_name, normal_avg_temp_c, normal_max_temp_c, normal_min_temp_c,
            normal_precip_mm, normal_humidity_pct, normal_wind_ms,
            normal_cloud_cover_pct, normal_rainy_days)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                month_name             = VALUES(month_name),
                normal_avg_temp_c      = VALUES(normal_avg_temp_c),
                normal_max_temp_c      = VALUES(normal_max_temp_c),
                normal_min_temp_c      = VALUES(normal_min_temp_c),
                normal_precip_mm       = VALUES(normal_precip_mm),
                normal_humidity_pct    = VALUES(normal_humidity_pct),
                normal_wind_ms         = VALUES(normal_wind_ms),
                normal_cloud_cover_pct = VALUES(normal_cloud_cover_pct),
                normal_rainy_days      = VALUES(normal_rainy_days);
        """
        try:
            values = (month, month_name, normal_avg_temp_c, normal_max_temp_c,
                    normal_min_temp_c, normal_precip_mm, normal_humidity_pct,
                    normal_wind_ms, normal_cloud_cover_pct, normal_rainy_days)
            cursor.execute(query, values)
            self.mydb.commit()
            return True
        except Exception as e:
            print(f"Insert error (baseline month {month}): {e}")
            return False
        finally:
            cursor.close()
            
    # Inster daily forecast data into the 'daily_forecast' table with a reference to the corresponding season based on the month of the forecast date
    def insert_daily_forecast(self, forecast_date, year, month, month_name,
                           avg_temp_c, max_temp_c, min_temp_c, precip_mm,
                           precip_probability_pct, humidity_pct, wind_speed_ms,
                           wind_gust_ms, wind_direction, cloud_cover_pct,
                           visibility_km, uv_index, dewpoint_c, pressure_hpa,
                           weather_description, data_source):
        cursor = self.mydb.cursor()

        # Resolve season_id from month
        season = self.get_season_by_month(month)
        season_id = season["season_id"] if season else None

        query = """
            INSERT INTO daily_forecast
            (season_id, forecast_date, year, month, month_name, avg_temp_c,
            max_temp_c, min_temp_c, precip_mm, precip_probability_pct,
            humidity_pct, wind_speed_ms, wind_gust_ms, wind_direction,
            cloud_cover_pct, visibility_km, uv_index, dewpoint_c,
            pressure_hpa, weather_description, data_source)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                season_id               = VALUES(season_id),
                avg_temp_c              = VALUES(avg_temp_c),
                max_temp_c              = VALUES(max_temp_c),
                min_temp_c              = VALUES(min_temp_c),
                precip_mm               = VALUES(precip_mm),
                precip_probability_pct  = VALUES(precip_probability_pct),
                humidity_pct            = VALUES(humidity_pct),
                wind_speed_ms           = VALUES(wind_speed_ms),
                wind_gust_ms            = VALUES(wind_gust_ms),
                wind_direction          = VALUES(wind_direction),
                cloud_cover_pct         = VALUES(cloud_cover_pct),
                visibility_km           = VALUES(visibility_km),
                uv_index                = VALUES(uv_index),
                dewpoint_c              = VALUES(dewpoint_c),
                pressure_hpa            = VALUES(pressure_hpa),
                weather_description     = VALUES(weather_description),
                data_source             = VALUES(data_source);
        """
        try:
            values = (season_id, forecast_date, year, month, month_name,
                    avg_temp_c, max_temp_c, min_temp_c, precip_mm,
                    precip_probability_pct, humidity_pct, wind_speed_ms,
                    wind_gust_ms, wind_direction, cloud_cover_pct,
                    visibility_km, uv_index, dewpoint_c, pressure_hpa,
                    weather_description, data_source)
            cursor.execute(query, values)
            self.mydb.commit()
            return True
        except Exception as e:
            print(f"Insert error (forecast {forecast_date}): {e}")
            return False
        finally:
            cursor.close()

    # Utility methods for debugging and verification
    def print_databases(self):
        print("Fetching and printing all databases...")
        self.mycursor.execute("SHOW DATABASES")
        for db in self.mycursor:
            print(db)

    def print_tables(self, database_name):
        print(f"Fetching and printing all tables in the database: {database_name}...")
        self.mycursor.execute(f"USE {database_name}")
        self.mycursor.execute("SHOW TABLES")
        for table in self.mycursor:
            print(table)
    
    # TODO: remove method to delete database after testing is complete
    def delete_database(self, database_name):
        cursor = self.mydb.cursor()
        try:
            cursor.execute(f"DROP DATABASE IF EXISTS {database_name}")
            self.mydb.commit()
            print(f"Database '{database_name}' deleted successfully.")
        except Exception as e:
            print(f"Failed to delete database '{database_name}': {e}")
            raise
        finally:
            cursor.close()