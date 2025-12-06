from APRTF import R, E

class Job:
    def __init__(self, id, p, r):
        self.id = id #job name like Alpha, Beta
        self.p = p
        self.r = r
        self.completion_time = 0
        self.start_time = 0
        self.prtf_val = 0
        self.tmp_prtf = 0


partial_schedule = []  # some jobs
# first try to kill new node with dominance criteria
# supplementary nodes th11; dom: corr1, thm 6, 7, 9, 10,
# +dominance of active subset
# Jobs N = {1, 2, ..., n}, release date r_i, processing time p_i,
# completion_time C_i(\sigma), flow time F_i(\sigma) = C_i(\sigma) - r_i
# R_i(\delta) = max(\delta, r_i) earliest beginning time job i
# E_i(\delta) = R_i + p_i earliest completion time job i
# K = partial schedule, J(K) = jobs in K,
# \phi(K) = completion time last job in K
# K|i = new partial schedule K+i;
# \Sigma(K, i) ist partial schedule K|i + optimal schedule von jobs N - J(K|i)
# von Moment phi(K|i)
# \Delta_i = Completion time job immedieatly preceeding job i
# Dominanzkriterien: Kriterium, dass \Sigma(K, i) dominiert wird von irgendwem

# THM 6: \exists j \in N - J(K): j != i; E_i(\Phi(K)) >= E_j(\Phi(K));
# E_i(Phi(K))-E_j(Phi(K)) >= (p_i - p_j)[|N-J(K)| - 1]

# THM 7: \exists j \in N - J(K): j != i; E_i(\Phi(K)) <= E_j(\Phi(K));
# (E_i(Phi(K))-E_j(Phi(K)))([|N-J(K)|]) >= (p_i - p_j) ACHTUNG HIER KEINE -1

# THM 9: \exists j \in J(K): j!= i; E_i(\delta_j) <= E_j(\delta_j); E_i(\delta_j)- E_j(\delta_j) <= (p_i - p_j) * |N - J(K)|
# THM 10: \exists j \in J(K) in k-ter Position: p_i >= p_j; p_i - p_j >= (E_i(\delta_j)- E_j(\delta_j)) * (|J(K)| - k + 2)


# Thm 6/7, True iff dominated
def domThmAB(remaining_jobs: List, added_job: Job, current_schedule_finish: int):
    for j in remaining_jobs:
        if ((E(added_job, current_schedule_finish) >= E(j, current_schedule_finish) and
            E(added_job, current_schedule_finish) - E(j, current_schedule_finish) >= (added_job.p - j.p) * (len(remaining_jobs))) or
            ((E(added_job, current_schedule_finish) <= E(j, current_schedule_finish)) and
            (E(added_job, current_schedule_finish) - E(j, current_schedule_finish)) * (len(remaining_jobs) - 1) >= (added_job.p - j.p))):
            return True
    return False


def domThmCB(current_schedule : List, i : Job, remaining_jobs: List):
    for j in range(0, len(current_schedule)):
        delta_j = 0 if (j == 0) else current_schedule[j-1].completion_time
        if (E(i, delta_j) <= E(j, delta_j) and E(i, delta_j) - E(j, delta_j) <= (i.p - j.p) * (len(remaining_jobs) - 1)):
            return True
        if (i.p >= j.p and i.p - j.p >= (E(i, delta_j) - E(j, delta_j)) * (len(current_schedule) - j + 2)):
            return True
    return False
