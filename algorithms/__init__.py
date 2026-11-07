from algorithms.fcfs import FCFSScheduler
from algorithms.sjf import SJFScheduler
from algorithms.srtf import SRTFScheduler
from algorithms.priority import PriorityScheduler
from algorithms.round_robin import RoundRobinScheduler


def create_all_schedulers(time_quantum=4):
    return [
        FCFSScheduler(),
        SJFScheduler(),
        SRTFScheduler(),
        PriorityScheduler(preemptive=False),
        PriorityScheduler(preemptive=True),
        RoundRobinScheduler(time_quantum),
    ]