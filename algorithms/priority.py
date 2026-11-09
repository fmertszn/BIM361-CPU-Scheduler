from scheduler import Scheduler


class PriorityScheduler(Scheduler):

    def __init__(self, preemptive=False):
        super().__init__()
        self.preemptive = preemptive
        self.name = "Priority (kesintili)" if preemptive else "Priority"

    def reset(self):
        """Hazır kuyruğunu sıfırlar (her simülasyon başında çağrılır)."""
        self.ready_queue.clear()

    def get_time_quantum(self):
        """Priority algoritması zaman dilimi (quantum) kullanmaz."""
        return None

    def add_process(self, process):
        """Yeni gelen süreci hazır kuyruğuna ekler."""
        self.ready_queue.add(process)

    def select_next(self, current_time):
        """Kuyruktan öncelik değeri en düşük (en yüksek öncelik) süreci seçer.

        Eşitlik durumunda geliş zamanı (arrival_time), ardından süreç kimliği
        (process_id) kullanılarak deterministik seçim yapılır.
        """
        if self.ready_queue.is_empty():
            return None
        return self.ready_queue.pop_min(
            key=lambda p: (p.priority, p.arrival_time, p.process_id)
        )

    def should_preempt(self, running_process, current_time):
        """Kesinti gerekip gerekmediğini kontrol eder.

        Yalnızca ``preemptive=True`` modunda aktiftir. Hazır kuyrukta
        çalışan süreçten daha yüksek öncelikli (daha düşük priority değeri)
        bir süreç varsa kesinti yapılır.
        """
        if not self.preemptive:
            return False
        if self.ready_queue.is_empty():
            return False
        best = self.ready_queue.peek_min(
            key=lambda p: (p.priority, p.arrival_time, p.process_id)
        )
        return best.priority < running_process.priority
