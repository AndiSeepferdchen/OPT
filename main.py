from data_loader import load_processing_and_release
from APRTF import get_project_jobs, APRTF
#%%
##processing_times, release_dates = load_processing_and_release("./data/term_project_data.csv")
    
##project_jobs = get_project_jobs(processing_times, release_dates)

##APRTF(project_jobs, start_delta=0)
#%%
import sys

def main():
    # Load data
    processing_times, release_dates = load_processing_and_release("./data/term_project_data.csv")
    project_jobs = get_project_jobs(processing_times, release_dates)
    report_filename = "scheduling_report.txt"

    original_stdout = sys.stdout 
    try:
        with open(report_filename, 'w', encoding='utf-8') as f:
            sys.stdout = f
            APRTF(project_jobs, start_delta=0)
            f.flush() 
    except Exception as e:
        print(f"An error occurred during APRTF execution: {e}")
    finally:
        sys.stdout = original_stdout
        
    print("\nDone!")
    
if __name__ == "__main__":
    main()