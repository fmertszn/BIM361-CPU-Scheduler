from ready_queue import ReadyQueue

class Scheduler:
    """Tüm algoritmaların ortak temel sınıfı."""
    name = "Scheduler"

    def __init__(self):
        self.ready_queue = ReadyQueue()

    def add_process(self, process):
        self.ready_queue.add(process)

    def select_next(self, current_time):
        raise NotImplementedError(f"{self.name}.select_next")

    def should_preempt(self, running_process, current_time):
        return False

    def get_time_quantum(self):
        return None

    def reset(self):
        self.ready_queue.clear()


class FCFSScheduler(Scheduler):
    name = "FCFS"

    def select_next(self, current_time):
        raise NotImplementedError("FCFS.select_next")


class SJFScheduler(Scheduler):
    name = "SJF"

    def select_next(self, current_time):
        raise NotImplementedError("SJF.select_next")


class SRTFScheduler(Scheduler):
    name = "SRTF"

    def select_next(self, current_time):
        raise NotImplementedError("SRTF.select_next")

    def should_preempt(self, running_process, current_time):
        raise NotImplementedError("SRTF.should_preempt")


class PriorityScheduler(Scheduler):
    def __init__(self, preemptive=False):
        super().__init__()
        self.preemptive = preemptive
        self.name = "Priority (kesintili)" if preemptive else "Priority"

    def select_next(self, current_time):
        raise NotImplementedError("Priority.select_next")

    def should_preempt(self, running_process, current_time):
        if not self.preemptive:
            return False
        raise NotImplementedError("Priority.should_preempt")


class RoundRobinScheduler(Scheduler):
    def __init__(self, time_quantum=4):
        super().__init__()
        if time_quantum <= 0:
            raise ValueError("Quantum pozitif olmalı")
        self.time_quantum = time_quantum
        self.name = f"Round Robin (q={time_quantum})"

    def get_time_quantum(self):
        return self.time_quantum

    def select_next(self, current_time):
        raise NotImplementedError("RoundRobin.select_next")


def create_all_schedulers(time_quantum=4):
    return [
        FCFSScheduler(),
        SJFScheduler(),
        SRTFScheduler(),
        PriorityScheduler(preemptive=False),
        PriorityScheduler(preemptive=True),
        RoundRobinScheduler(time_quantum),
    ]