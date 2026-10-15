import mysql.connector
from mysql.connector import Error

def setup_database():
    try:
        host = input("Enter MySQL Host [localhost]: ") or "localhost"
        user = input("Enter MySQL Username [root]: ") or "root"
        password = input("Enter MySQL Password: ")

        print("\nConnecting to MySQL server...")
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password
        )

        if connection.is_connected():
            cursor = connection.cursor()
            
            print("Creating database 'space_invaders_aseniero' if it doesn't exist...")
            cursor.execute("CREATE DATABASE IF NOT EXISTS space_invaders_danganan")
            
            print("Using 'space_invaders_danganan'...")
            cursor.execute("USE space_invaders_danganan")
            
            print("Creating 'players' table...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS players (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password_hash VARCHAR(64) DEFAULT NULL,
                    ship_color VARCHAR(20) DEFAULT 'orange',
                    player_title VARCHAR(50) DEFAULT 'Genin Shinobi',
                    control_scheme VARCHAR(10) DEFAULT 'arrows',
                    difficulty VARCHAR(10) DEFAULT 'normal',
                    btn_left_enabled TINYINT(1) DEFAULT 1,
                    btn_right_enabled TINYINT(1) DEFAULT 1,
                    btn_fire_enabled TINYINT(1) DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            print("Creating 'scores' table...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scores (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    player_id INT,
                    score INT NOT NULL,
                    achieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (player_id) REFERENCES players(id) ON DELETE CASCADE
                )
            """)
            
            connection.commit()
            print("\nShinobi Database setup complete successfully!")
            
    except Error as e:
        print(f"\nError while connecting to MySQL: {e}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    setup_database()