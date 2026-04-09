import os
from dotenv import load_dotenv
from db_helper import DBHelper

def main():

    print("Initializing project...")
    print("Loading environment variables...")
    load_dotenv()
    
    # Fetching database credentials from environment variables
    db_host = os.getenv("DB_HOST")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    print("Database credentials loaded successfully... ")
    
    # Creating an instance of DBHelper with the loaded credentials
    db_helper = DBHelper(db_host, db_user, db_password)
    db_helper.prepare_database(os.getenv("DB_NAME"))
    
    

    
if __name__ == "__main__":
    main()