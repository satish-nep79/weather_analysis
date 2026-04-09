import mysql.connector

class DBHelper:
    
    
    def __init__(self, host, user, password):
        # Establishing a connection to the MySQL database using the provided credentials
        print("Establishing a connection to the MySQL database...")
        self.mydb = mysql.connector.connect(
            host=host,
            user=user,
            password=password
        )
        print("Connection to the MySQL database established successfully...")
        self.mycursor = self.mydb.cursor()
        
        
    # Preparing the database for use:
    # - Creating the database if it does not already exist
    # - Selecting the database for subsequent operations
    # - Executing the necessary SQL commands to set up the database structure (e.g., creating tables)
    # - Handling any exceptions that may occur during the database setup process and providing appropriate feedback
    # This method ensures that the database is ready for use before any further operations are performed.
    def prepare_database(self, database_name):
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
        queries = [
            # 1. SEASONS (Independent)
            """
            CREATE TABLE IF NOT EXISTS seasons (
                season_id INT AUTO_INCREMENT PRIMARY KEY,
                season_name VARCHAR(20) NOT NULL UNIQUE,
                months_range VARCHAR(50),
                tourism_level VARCHAR(20),
                avg_temp_c FLOAT,
                avg_precip_mm FLOAT,
                avg_humidity_pct FLOAT,
                avg_cloud_cover_pct FLOAT,
                rainy_days_per_month INT
            ) ENGINE=InnoDB;
            """,

            # 2. CLIMATE BASELINE (Independent - Monthly Norms)
            """
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
            """
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
            """
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
        ]
        
        try:
            for command in queries:
                cursor.execute(command)
            self.mydb.commit()
            print("Database schema initialized successfully.")
            self.print_tables(database_name=self.mydb.database)
        except Exception as e:
            print(f"Database schema initialization failed: {e}")
            raise
        finally:
            cursor.close()
    
    
    
        
    

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