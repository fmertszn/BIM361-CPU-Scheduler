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
