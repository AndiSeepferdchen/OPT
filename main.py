import heapq
import sys
from copy import copy
from APRTF import PRTF_Andi
# Import your modules
from data_loader import load_processing_and_release
from srpt import calculate_lb_srpt
from dominance_criteria import checkFActive, domThmAB, domThmCB

# --- 1. Data Structures ---

class Job:
    def __init__(self, id, p, r):
        self.id = id #job name like Alpha, Beta
        self.p = p
        self.r = r
        self.completion_time = 0 #I think we dont necessarily need the other stuff here since its stored in the nodes now
        self.start_time = 0
        self.prtf_val = 0
        self.tmp_prtf = 0


class Node:
    def __init__(self, parent, job, lb, flow, completion_time, scheduled_indices):
        self.parent = parent
        self.job = job # The job scheduled at this step
        self.lb = lb
        self.current_flow = flow
        self.completion_time = completion_time

        # Set of scheduled job IDs (integers) for const time lookups
        self.scheduled_indices = scheduled_indices

    # PQ comps:
    # 1. Lower Bound (smallest first)
    # 2. Number of scheduled jobs (largest first -> deeper in tree)
    def __lt__(self, other):
        if self.lb != other.lb:
            return self.lb < other.lb
        return len(self.scheduled_indices) > len(other.scheduled_indices)


def calculate_initial_upper_bound(jobs):
    return PRTF_Andi(jobs)

def solve_bb_c(all_jobs):

    # Sort jobs by ID for consistent indexing -> indices 0..n-1 to track jobs
    for idx, j in enumerate(all_jobs):
        j.original_index = idx

    global_ub = calculate_initial_upper_bound(all_jobs)
    print(f"Initial Upper Bound: {global_ub}")

    # Root Node: Dummy node (Time 0, Flow 0, No jobs)
    root = Node(None, None, 0, 0, 0, set())

    # Priority Queue
    pq = []
    heapq.heappush(pq, root)

    nodes_explored = 0

    while pq:
        # Gbest node
        node = heapq.heappop(pq)

        # If LB arleady worse than global opt we can instantly kill this node
        if node.lb >= global_ub:
            continue

        nodes_explored += 1
        if nodes_explored % 100 == 0:
            print(f"Nodes: {nodes_explored}, PQ Size: {len(pq)}, Current UB: {global_ub}, Best LB: {node.lb}")

        unscheduled_jobs = [j for j in all_jobs if j.original_index not in node.scheduled_indices]

        # No jobs left --> we have complete solution
        if not unscheduled_jobs:
            if node.current_flow < global_ub:
                global_ub = node.current_flow
                print(f"** New Best Solution Found: {global_ub} **")
            continue

        # Try to schedule each available job
        for candidate in unscheduled_jobs:

            # Dominance checks:

            # 1. F-Active (Corr 1)
            prev_prev_time = node.parent.completion_time if node.parent else 0
            if not checkFActive(node.job, candidate, prev_prev_time):
                continue # Prune: Sequence is not F-Active

            # 2. Theorems 6 & 7 (Implemented it in same function since theyre very similar)
            if domThmAB(unscheduled_jobs, candidate, node.completion_time):
                continue # Prune: Dominated by another unscheduled job

            # 3. Theorems 9 & 10 (Again implemented in same func since very similar)
            if domThmCB(node, candidate, len(unscheduled_jobs)):
                continue

            # Added job -> new timings
            start_time = max(node.completion_time, candidate.r)
            finish_time = start_time + candidate.p
            added_flow = finish_time - candidate.r
            new_current_flow = node.current_flow + added_flow

            # Prune if partial flow already exceeds UB (rare but possible)
            if new_current_flow >= global_ub:
                continue

            # SRPT LB on remaining jobs (excl new job)
            remaining_after_candidate = [j for j in unscheduled_jobs if j != candidate]

            srpt_remaining_flow, preemption_occurred = calculate_lb_srpt(
                remaining_after_candidate,
                finish_time # Current time becomes completion of candidate
            )

            new_lb = new_current_flow + srpt_remaining_flow

            # Prune based on Lower Bound
            if new_lb >= global_ub:
                continue


            # Test optimality (if SRPT doesnt have preemtipon)
            if not preemption_occurred:
                if new_lb < global_ub:
                    global_ub = new_lb
                    print(f"** Solution Pruned via Optimality Test: {global_ub} **")
                continue

            # Branch
            new_indices = node.scheduled_indices.copy()
            new_indices.add(candidate.original_index)

            child_node = Node(
                parent=node,
                job=candidate,
                lb=new_lb,
                flow=new_current_flow,
                completion_time=finish_time,
                scheduled_indices=new_indices
            )

            heapq.heappush(pq, child_node)
    return global_ub


def main():
    processing_times, release_dates = load_processing_and_release("./data/term_project_data.csv")
    # Create Job Objects
    jobs = []
    for i in range(len(processing_times)):
        jobs.append(Job(i, processing_times[i], release_dates[i]))

    # Limit jobs for testing
    test_jobs = jobs

    print(f"Num jobs: {len(test_jobs)}")
    final_flow = solve_bb_c(test_jobs)
    print(f"Opt solution: {final_flow}")


if __name__ == "__main__":
    main()
