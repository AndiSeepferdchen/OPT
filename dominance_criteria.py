from typing import List



def get_R(job, time):
    return max(time, job.r)


def get_E(job, time):
    return get_R(job, time) + job.p


def get_PRTF(job, time):
    # PRTF(i, t) = 2*max(t, r_i) + p_i
    return 2 * max(time, job.r) + job.p


def checkFActive(last_job, new_job, completion_time_of_job_before_last):
    if last_job is None:
        return True
    t = completion_time_of_job_before_last

    cond1 = get_R(last_job, t) < get_R(new_job, t)
    cond2 = get_PRTF(last_job, t) <= get_PRTF(new_job, t)

    return cond1 or cond2



def domThmAB(remaining_jobs: List, added_job, current_time: int):
    """
    Theorems 6 and 7
    """
    n_minus_k = len(remaining_jobs)
    E_i = get_E(added_job, current_time)

    for j in remaining_jobs:
        if j.id == added_job.id:
            continue

        E_j = get_E(j, current_time)

        # Theorem 6
        if E_i >= E_j:
            lhs = E_i - E_j
            rhs = (added_job.p - j.p) * (n_minus_k - 1)

            if lhs > rhs:
                return True
            elif lhs == rhs and added_job.id > j.id:
                return True

        # Theorem 7
        if E_i <= E_j:
            lhs = E_i - E_j
            lhs_scaled = lhs * n_minus_k
            rhs = added_job.p - j.p

            if lhs_scaled > rhs:
                return True
            elif lhs_scaled == rhs and added_job.id > j.id:
                return True

    return False


def domThmCB(current_node, new_job, num_unscheduled_jobs):
    """
    Theorems 9 and 10
    """
    job_i = new_job
    curr = current_node
    dist_from_end = 2

    while curr is not None and curr.job is not None:
        job_j = curr.job

        if curr.parent:
            delta_j = curr.parent.completion_time
        else:
            delta_j = 0

        E_i = get_E(job_i, delta_j)
        E_j = get_E(job_j, delta_j)

        if E_i <= E_j:
            lhs = E_i - E_j
            rhs = (job_i.p - job_j.p) * num_unscheduled_jobs

            if lhs < rhs:
                return True
            elif lhs == rhs and job_j.id > job_i.id:
                return True

        if job_i.p >= job_j.p:
            lhs = job_i.p - job_j.p
            rhs = (E_i - E_j) * dist_from_end

            if lhs > rhs:
                return True
            elif lhs == rhs and job_j.id > job_i.id:
                return True

        curr = curr.parent
        dist_from_end += 1

    return False
