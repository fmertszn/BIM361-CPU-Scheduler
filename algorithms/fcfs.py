from ready_queue import ReadyQueue


class FCFSScheduler:
    """First-Come, First-Served (FCFS) Zamanlayıcı (Simulator Uyumlu)."""

    def __init__(self):
        self.name = "FCFS"
        self.ready_queue = ReadyQueue()

    def reset(self):
        """Hazır kuyruğunu sıfırlar."""
        self.ready_queue.clear()

    def get_time_quantum(self):
        """FCFS preemptive olmadığı için kuantum değeri yoktur."""
        return None

    def add_process(self, process):
        """Yeni gelen süreci hazır kuyruğuna ekler."""
        self.ready_queue.add(process)

    def select_next(self, current_time):
        """Kuyruktan sıradaki ilk süreci seçer (Geliş sırasına göre)."""
        if self.ready_queue.is_empty():
            return None
        return self.ready_queue.pop_first()

    def should_preempt(self, running, current_time):
        """FCFS kesintisizdir (non-preemptive), bu yüzden hep False döner."""
        return False