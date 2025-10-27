import os
import datetime
import zipfile
import shutil

# 🗄️ Database Configuration
DB_NAME = "welvision_db"
USER = "root"
PASSWORD = "root"
BACKUP_DIR = "C:/welvision_backups"  # Change to your preferred location
MYSQLDUMP_PATH = "mysqldump"  # or full path: "C:/Program Files/MySQL/MySQL Server 8.0/bin/mysqldump.exe"

# 📅 Timestamp for backup file
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
sql_filename = f"{DB_NAME}_backup_{timestamp}.sql"
sql_path = os.path.join(BACKUP_DIR, sql_filename)
zip_filename = f"{DB_NAME}_backup_{timestamp}.zip"
zip_path = os.path.join(BACKUP_DIR, zip_filename)

# 🗂️ Ensure backup folder exists
os.makedirs(BACKUP_DIR, exist_ok=True)

# 🧠 Backup command
dump_command = f'"{MYSQLDUMP_PATH}" -u {USER} -p{PASSWORD} {DB_NAME} > "{sql_path}"'

print(f"\n📦 Backing up database '{DB_NAME}' ...")
os.system(dump_command)

# ✅ Compress the backup into ZIP
if os.path.exists(sql_path):
    print(f"🗜️ Compressing backup into ZIP: {zip_filename}")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(sql_path, os.path.basename(sql_path))
    os.remove(sql_path)  # delete original .sql after compressing
    print("✅ Backup completed and compressed successfully.")
    print(f"📁 Saved at: {zip_path}")
else:
    print("❌ Backup failed. Check MySQL credentials or PATH configuration.")
