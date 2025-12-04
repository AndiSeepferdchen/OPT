#%%
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
#%%
#Scheduling function: job1=Alpha, job2=Beta, delta=Current Time t, 
#calculate Completion Time, Delay tau, Idle Time D1/D2
def calculate_sequence_metrics(job1, job2, delta):
    # Job1 S =max(currnt t, released date_j1)
    S1 = max(delta, job1.r)
    C1 = S1 + job1.p  #Completion Time

    # Job2
    S2 = max(C1, job2.r)
    C2 = S2 + job2.p  #Completion Time_j2 = C_max to done j1+j2

    # Baseline C2: Completion Time_j2 if Scheduling j2 first, /j2 -> j1/
    S2_base = max(delta, job2.r)
    C2_base = S2_base + job2.p

# Loss & Idle Time
    # Loss: Delay (tau) of j2 if "j1 -> j2" = C2_j1->j2 - C2_base << This is E(earliest complete time)
    tau = C2 - C2_base

    # Idle Time D1 between C1 and S2 if "j1 -> j2" (Actual Idle Time)
    D1 = S2 - C1
    # if D1 > 0 means machine have to wait Release Date (r) of job2

    # Idle Time D2 (Non-Avoidable Idle Time if /j2 -> j1/) = the time waiting for r_j2
    D2 = max(job2.r - delta, 0)

    return {
        "sequence": f"{job1.id} -> {job2.id}",
        "C_max": C2,
        "tau": tau,
        "D1": D1,
        "D2": D2,
        "C1": C1,
        "S1": S1,
        "S2": S2
    }
#%%
# Data Loading
def get_project_jobs(processing_times, release_dates):

    jobs = []
    num_jobs = len(processing_times)
    for i in range(num_jobs):
        p = processing_times[i]
        r = release_dates[i]
        jobs.append(Job(id=f"Job_{i+1}", p=p, r=r))

    return jobs
#%%
# APRTF
def get_release_date(job_object):
    return job_object.r

def get_processing_time(job_object):
    return job_object.p

def APRTF(all_jobs, start_delta=0):
    # Sorted all jobs by Release Date (r), from the smallest r
    # use release_date from get_release_date
    remaining_jobs = sorted(all_jobs, key=get_release_date)
    scheduled_jobs = []
    current_time = start_delta

    print("=====================================")
    print("--- Start Scheduling ---")
    print("=====================================")

    while remaining_jobs:
        #list ready jobs at current t
        ready_jobs = [job for job in remaining_jobs if job.r <= current_time]
        if not ready_jobs:
            #if no ready jobs, skip to Release Date of next sorted job
            current_time = remaining_jobs[0].r
            print(f"\n[{current_time}]:**IDLE**. Advancing time to R={current_time} to wait for {remaining_jobs[0].id}")
            ready_jobs = [job for job in remaining_jobs if job.r <= current_time] # load ready jobs at the new current time 

        # APRTF Decision
        best_job_to_schedule = None
        if len(ready_jobs) == 1: # if there is only one ready job
            best_job_to_schedule = ready_jobs[0]
            print(f"\n[{current_time}]: Only one ready job: Selecting {best_job_to_schedule.id}")

        else: # if there are more than one ready job
            print(f"\n[{current_time}]: Multiple ready jobs: {[job.id for job in ready_jobs]}. Comparing metrics....")
            # Step1: Choose the job that has Shortest Processing Time (SPT),
            # Step2: Choose the job that has minimum Total Loss (tau)
            best_job_to_schedule = min(ready_jobs, key=get_processing_time)
            if len(ready_jobs) >= 2:
                sorted_by_p = sorted(ready_jobs, key=get_processing_time)
                job_alpha = sorted_by_p[0] # Job1 identified by SPT (the smallest p_time)
                job_beta = sorted_by_p[1] # Job2 identified by SPT (the second smallest p_time)

                # compare j1 & j2 parameters
                metrics_alpha_first = calculate_sequence_metrics(job_alpha, job_beta, current_time)     
                metrics_beta_first = calculate_sequence_metrics(job_beta, job_alpha, current_time)

                tau_alpha = metrics_alpha_first["tau"]
                tau_beta = metrics_beta_first["tau"]

                if tau_alpha <= tau_beta:
                    final_choice_id = job_alpha.id
                else:
                    final_choice_id = job_beta.id

                best_job_to_schedule = [job for job in ready_jobs if job.id == final_choice_id][0]

                print(f"  --- APRTF Metric Comparison (Alpha={job_alpha.id}, Beta={job_beta.id}) ---")
                print(f"  If scheduling {job_alpha.id} first: Loss (τ_{job_beta.id}) = {tau_alpha}")
                print(f"  If scheduling {job_beta.id} first: Loss (τ_{job_alpha.id}) = {tau_beta}")
                print(f"  **Decision (Min Loss):** Schedule {final_choice_id} first")
            else:
                 pass

        # remove job1,job2 from Job dataset
        remaining_jobs.remove(best_job_to_schedule)

        # calculate C & S of the chosen job
        start_time = max(current_time, best_job_to_schedule.r)
        completion_time = start_time + best_job_to_schedule.p

        # Store result
        best_job_to_schedule.start_time = start_time
        best_job_to_schedule.completion_time = completion_time
        scheduled_jobs.append(best_job_to_schedule)

        # Update current time
        current_time = completion_time
        print(f"  >> Schedule: {best_job_to_schedule.id} | p={best_job_to_schedule.p}, r={best_job_to_schedule.r}")
        print(f"  >> Start at: {start_time} | Complete at: {completion_time}")
        print(f"  >> Machine Time Updated to: {current_time}")

    # Final result
    print("\n" + "=" * 60)
    print("--- Scheduling Results Summary ---")
    print("=" * 60)
    C_max = 0
    total_flow_time = 0 # Flow Time = C - r
    for job in scheduled_jobs:
        flow_time = job.completion_time - job.r
        total_flow_time += flow_time
        C_max = max(C_max, job.completion_time)
        print(f"  {job.id} | Start: {job.start_time} | Complete: {job.completion_time} | Flow Time: {flow_time}")

    print("----------------------------------")
    print(f"Total Completion Time (C_max): {C_max}")
    print(f"Average Flow Time: {total_flow_time / len(scheduled_jobs):.2f}") #2 digit number
    print("----------------------------------")

    return scheduled_jobs


def R(i, delta):
    return max(delta, i.r)

def E(i, delta):
    return R(i, delta) + i.p

def prtf(i, delta):
        return 2 * R(i, delta) + i.p


def update_prtf_values(jobs, delta):
    for job in jobs:
        job.tmp_prtf = prtf(job, delta)
    return jobs


def PRTF_Andi(all_jobs):   
    remaining_jobs = all_jobs
    delta = 0
    sum_of_completion_times = 0
    scheduled_jobs = []

    while len(remaining_jobs) != 1:
        update_prtf_values(all_jobs, delta)

        alpha = min(
            enumerate(remaining_jobs),
            key=lambda x: (x[1].tmp_prtf, x[1].r, x[0]))[1]
        beta = min(remaining_jobs, key=lambda x: (x.r, x.p))
        if alpha.r <= R(beta, delta):
            sum_of_completion_times += alpha.tmp_prtf
            print(f"  >> Schedule: {alpha.id} | p={alpha.p}, r={alpha.r}")
            start_time = R(beta, delta)
            complete_time = E(beta, delta)
            alpha.start_time = start_time
            alpha.completion_time = complete_time
            print(f"  >> Start at: {start_time} | Complete at: {complete_time}")
            delta = E(alpha, delta)
            print(f"  >> Machine Time Updated to: {delta}")
            remaining_jobs.remove(alpha)
            scheduled_jobs.append(alpha)
        else:
            mu = len(remaining_jobs) - 2
            tau = min((job for job in remaining_jobs if job not in (alpha, beta)), key=lambda x: x.r).r
        
            if R(beta, delta) - R(alpha, delta) < mu * min( R(alpha, delta) - R(beta, delta), E(beta, E(alpha, delta)) - tau):
                sum_of_completion_times += beta.tmp_prtf
                print(f"  >> Schedule: {beta.id} | p={beta.p}, r={beta.r}")
                start_time = R(beta, delta)
                complete_time = E(beta, delta)
                beta.start_time = start_time
                beta.completion_time = complete_time
                print(f"  >> Start at: {start_time} | Complete at: {complete_time}")
                delta = E(beta, delta)
                print(f"  >> Machine Time Updated to: {delta}")
                remaining_jobs.remove(beta)
                scheduled_jobs.append(beta)
            else:
                sum_of_completion_times += alpha.tmp_prtf
                print(f"  >> Schedule: {alpha.id} | p={alpha.p}, r={alpha.r}")
                start_time = R(beta, delta)
                complete_time = E(beta, delta)
                alpha.start_time = start_time
                alpha.completion_time = complete_time
                print(f"  >> Start at: {start_time} | Complete at: {complete_time}")
                delta = E(alpha, delta)
                print(f"  >> Machine Time Updated to: {delta}")
                remaining_jobs.remove(alpha)
                scheduled_jobs.append(alpha)

    sum_of_completion_times += remaining_jobs[0].tmp_prtf
    start_time = R(remaining_jobs[0], delta)
    complete_time = E(remaining_jobs[0], delta)
    remaining_jobs[0].start_time = start_time
    remaining_jobs[0].completion_time = complete_time
    print(f"  >> Schedule: {remaining_jobs[0].id} | p={remaining_jobs[0].p}, r={remaining_jobs[0].r}")
    print(f"  >> Start at: {R(remaining_jobs[0], delta)} | Complete at: {E(remaining_jobs[0], delta)}")
    delta = E(remaining_jobs[0], delta)
    print(f"  >> Machine Time Updated to: {delta}")
    scheduled_jobs.append(remaining_jobs[0])
    remaining_jobs.remove(remaining_jobs[0])

    # Final result
    print("\n" + "=" * 60)
    print("--- Scheduling Results Summary ---")
    print("=" * 60)
    C_max = 0
    total_flow_time = 0 # Flow Time = C - r
    for job in scheduled_jobs:
        flow_time = job.completion_time - job.r

        total_flow_time += flow_time
        C_max = max(C_max, job.completion_time)
        print(f"  {job.id} | Start: {job.start_time} | Complete: {job.completion_time} | Flow Time: {flow_time}")

    print("----------------------------------")
    print(f"Total Completion Time (C_max): {C_max}")
    print(f"Average Flow Time: {total_flow_time / len(scheduled_jobs):.2f}") #2 digit number
    print("----------------------------------")
    return scheduled_jobs