import heapq

def calculate_lb_srpt(unscheduled_jobs, current_time):
    """
    Simulates SRPT on a set of unscheduled jobs.

    Args:
        unscheduled_jobs: List of objects/dicts with .r (release) and .p (processing)
                          or tuples (r, p, id).
        current_time: The completion time of the last scheduled job (the 'now').

    Returns:
        (lower_bound_flow, preemption_occurred)
        - lower_bound_flow: Sum of (Completion_Time - Release_Date) for all jobs.
        - preemption_occurred: Boolean, True if any job was stopped to run another.
    """

    # 1. Setup: Create a list of future events (job releases)
    # We sort by release date to process them in order.
    # Format: [release_date, processing_time, original_index]
    future_jobs = sorted(
        [[j.r, j.p, i] for i, j in enumerate(unscheduled_jobs)],
        key=lambda x: x[0],
        reverse=True # Reversed so we can pop from end (O(1))
    )

    # Priority Queue for available jobs: (remaining_time, release_date, original_index)
    ready_queue = []

    time = current_time
    total_flow = 0
    preemption_occurred = False

    # The job currently on the machine (None if idle)
    # Format: [remaining_time, release_date, original_index, original_p]
    active_job = None

    while future_jobs or ready_queue or active_job:

        # --- A. Update Ready Queue with Arrivals ---
        # Move all jobs released at or before 'time' into the ready queue
        while future_jobs and future_jobs[-1][0] <= time:
            r, p, idx = future_jobs.pop()
            # Push to heap: Sort primarily by remaining time (p)
            heapq.heappush(ready_queue, [p, r, idx, p])

        # --- B. Machine Idle Logic ---
        # If no job is active and queue is empty, jump to next release
        if not active_job and not ready_queue:
            if future_jobs:
                time = future_jobs[-1][0]
                continue
            else:
                break # Should not happen given outer while loop

        # --- C. Job Selection (The SRPT Decision) ---
        # If we are idle, pick best job.
        if not active_job:
            active_job = heapq.heappop(ready_queue)

        # If we are active, check if a newly arrived job (in queue) is better
        elif ready_queue:
            best_waiting = ready_queue[0]
            if best_waiting[0] < active_job[0]:
                # PREEMPTION HAPPENS HERE
                # We swap the active job back into the queue
                preemption_occurred = True
                heapq.heappush(ready_queue, active_job)
                active_job = heapq.heappop(ready_queue)

        # --- D. Simulation Step ---
        # Calculate time until next event: either current job finishes OR next job arrives
        time_to_finish = active_job[0]

        if future_jobs:
            time_to_arrival = future_jobs[-1][0] - time
            # If arrival is in the past (0 or negative), treat as 0
            time_to_arrival = max(0, time_to_arrival)
        else:
            time_to_arrival = float('inf')

        step = min(time_to_finish, time_to_arrival)

        # Advance clock and work
        time += step
        active_job[0] -= step # Reduce remaining time

        # --- E. Job Completion ---
        if active_job[0] == 0:
            # Job finished
            r_original = active_job[1]
            flow = time - r_original
            total_flow += flow
            active_job = None # Machine becomes free

    return total_flow, preemption_occurred
