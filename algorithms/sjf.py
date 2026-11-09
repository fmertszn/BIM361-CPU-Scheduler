from ready_queue import ReadyQueue


class SJFScheduler:
    """Shortest Job First (SJF - Non-Preemptive) Zamanlayıcı (Simulator Uyumlu)."""

    def __init__(self):
        self.name = "SJF"
        self.ready_queue = ReadyQueue()

    def reset(self):
        """Hazır kuyruğunu sıfırlar."""
        self.ready_queue.clear()

    def get_time_quantum(self):
        """Non-preemptive SJF için kuantum değeri yoktur."""
        return None

    def add_process(self, process):
        """Yeni gelen süreci hazır kuyruğuna ekler."""
        self.ready_queue.add(process)

    def select_next(self, current_time):
        """Kuyruktan çalışma süresi (burst_time) en kısa olan süreci seçer."""
        if self.ready_queue.is_empty():
            return None
        # En kısa burst_time'a sahip olanı seçiyoruz.
        # Eşitlik durumunda geliş zamanına (arrival_time) ve id'ye bakarak kararlı seçim yapıyoruz.
        return self.ready_queue.pop_min(
            key=lambda p: (p.burst_time, p.arrival_time, p.process_id)
        )

    def should_preempt(self, running, current_time):
        """Non-preemptive olduğu için çalışma anında kesme yapılmaz."""
        return False