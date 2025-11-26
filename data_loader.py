import csv
from pathlib import Path

def load_processing_and_release(file_path):
    processing_times = []
    release_dates = []
    # Directory of the current script
    root = Path(__file__).parent

    # Relative path to the data file
    csv_path = root / "data" / "term_project_data.csv"
    print(csv_path)
    with csv_path.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            processing_times.append(float(row["processing_time"]))
            release_dates.append(float(row["release_date"]))

    return processing_times, release_dates
