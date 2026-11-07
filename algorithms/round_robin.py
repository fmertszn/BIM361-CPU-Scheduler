from scheduler import Scheduler


class RoundRobinScheduler(Scheduler):
    """Her sürece eşit zaman dilimi verilir."""
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