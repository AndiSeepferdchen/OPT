from data_loader import load_processing_and_release
from APRTF import APRTF, PRTF_Andi
import sys

#Job Data Structure
class Job:
    def __init__(self, id, p, r):
        self.id = id #job name like Alpha, Beta
        self.p = p
        self.r = r
        self.completion_time = 0
        self.start_time = 0
        self.prtf_val = 0
        self.tmp_prtf = 0

def get_project_jobs(processing_times, release_dates):

    jobs = []
    num_jobs = len(processing_times)
    for i in range(num_jobs):
        p = processing_times[i]
        r = release_dates[i]
        jobs.append(Job(id=f"Job_{i+1}", p=p, r=r))

    return jobs

def bound_plausible_jobs(partial_schedule, delta, remaining_jobs):
    #TODO: find useful jobs to explore
    return remaining_jobs

list_of_final_job_orders = []

def iter_tree_builder(partial_schedule, delta, remaining_jobs):
    print(len(partial_schedule), delta, len(remaining_jobs))
    if len(remaining_jobs) == 0:
        list_of_final_job_orders.append(partial_schedule)
        return
    jobs_to_explore_list = bound_plausible_jobs(partial_schedule, delta, remaining_jobs)
    for job in jobs_to_explore_list:
        remaining = [x for x in jobs_to_explore_list if x != job]
        partial_schedule.append(job)
        if job.r > delta:
            delta = job.r
        delta += job.p
        iter_tree_builder(partial_schedule, delta, remaining)

def main():
    # Load data
    processing_times, release_dates = load_processing_and_release("./data/term_project_data.csv")
    project_jobs = get_project_jobs(processing_times, release_dates)
    ### ARPTF Code #####################################################################################

    # report_filename = "scheduling_report.txt"
    # print(sum(processing_times))
    # original_stdout = sys.stdout 
    # try:
    #     with open(report_filename, 'w', encoding='utf-8') as f:
    #         sys.stdout = f
    #         #APRTF(project_jobs[:100], start_delta=0)
    #         PRTF_Andi(project_jobs)
    #         f.flush() 
    # except Exception as e:
    #     print(f"An error occurred during APRTF execution: {e}")
    # finally:
    #     sys.stdout = original_stdout
        
    # print("\nDone!")
    ###################################################################################################

    ### Tree Construction Algorithm ###################################################################
    remaining_jobs = project_jobs[:2]
    partial_schedule = []
    delta = 0
    iter_tree_builder(partial_schedule, delta, remaining_jobs)
    # print(list_of_final_job_orders)


if __name__ == "__main__":
    main()
# %%
