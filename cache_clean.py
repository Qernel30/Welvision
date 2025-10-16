import os
import shutil

def delete_all_pycache(start_path="."):
    count = 0
    for root, dirs, files in os.walk(start_path):
        for dir_name in dirs:
            if dir_name == "__pycache__":
                full_path = os.path.join(root, dir_name)
                shutil.rmtree(full_path)
                print(f"🗑️ Deleted: {full_path}")
                count += 1
    print(f"\n✅ Done! Deleted {count} '__pycache__' folders.")

if __name__ == "__main__":
    delete_all_pycache(".")  # You can change "." to any folder path
