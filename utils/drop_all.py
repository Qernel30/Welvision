import mysql.connector

# Database connection configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "welvision_db"
}

def main():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        print(f"\nConnected to database: {DB_CONFIG['database']}")
        print("=" * 60)

        # Get all tables
        cursor.execute("SHOW TABLES;")
        tables = [row[0] for row in cursor.fetchall()]

        if not tables:
            print("⚠️  No tables found in the database.")
            return

        print(f"Found {len(tables)} tables to drop:")
        for t in tables:
            print(f" - {t}")

        # Disable foreign key checks
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")

        # Drop all tables
        for table in tables:
            try:
                cursor.execute(f"DROP TABLE IF EXISTS `{table}`;")
                print(f"✅ Dropped table: {table}")
            except Exception as e:
                print(f"❌ Failed to drop {table}: {e}")

        # Re-enable foreign key checks
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

        conn.commit()
        cursor.close()
        conn.close()

        print("\n🎯 All tables dropped successfully from welvision_db.")

    except mysql.connector.Error as err:
        print(f"\n❌ Database error: {err}")

if __name__ == "__main__":
    main()
