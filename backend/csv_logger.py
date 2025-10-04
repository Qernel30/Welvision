"""
CSV logging functionality for defect tracking
"""
import csv
import os


def initialize_bigface_csv():
    """Initialize the Bigface CSV file with headers."""
    print("Created csv for BF")
    if not os.path.exists("bigface_defects_log.csv"):
        with open("bigface_defects_log.csv", mode='w', newline='') as file:
            print(file)
            writer = csv.writer(file)
            writer.writerow(["roller_id", "defect_status", "plc status"])


def log_bigface_status(roller_id, defect_status, status):
    """Log the defect status of a roller in the Bigface CSV."""
    with open("bigface_defects_log.csv", mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([roller_id, defect_status, status])


def initialize_od_csv():
    """Initialize the od CSV file with headers."""
    print("Created csv for OD")
    
    if not os.path.exists("OD_defects_log.csv"):
        with open("od_defects_log.csv", mode='w', newline='') as file:
            print(file)
            writer = csv.writer(file)
            writer.writerow(["roller_id", "defect_status", "plc status", "od_dictionary"])


def log_od_status(roller_id, defect_status, status, od_dictionary):
    """Log the defect status of a roller in the OD CSV."""
    with open("od_defects_log.csv", mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([roller_id, defect_status, status, od_dictionary])
