from scheduler import Scheduler


class SRTFScheduler(Scheduler):
    """Shortest Remaining Time First (SRTF - Preemptive SJF) Zamanlayıcı."""
    name = "SRTF"

    def select_next(self, current_time):
        """Hazır kuyruğundan kalan çalışma süresi (remaining_time) en kısa olan süreci seçer."""
        if self.ready_queue.is_empty():
            return None
        return self.ready_queue.pop_min(
            key=lambda p: (p.remaining_time, p.arrival_time, p.process_id)
        )

    def should_preempt(self, running_process, current_time):
        """Kuyrukta kalan süresi mevcut çalışan süreçten daha kısa bir süreç varsa kesme (preempt) yapar."""
        if self.ready_queue.is_empty():
            return False
        shortest = self.ready_queue.peek_min(
            key=lambda p: (p.remaining_time, p.arrival_time, p.process_id)
        )
        return shortest.remaining_time < running_process.remaining_time
