from scheduler import Scheduler


class RoundRobinScheduler(Scheduler):
    def __init__(self, time_quantum=4):
        super().__init__()
        if time_quantum <= 0:
            raise ValueError("Quantum pozitif olmalı")
        self.time_quantum = time_quantum
        self.name = f"Round Robin (q={time_quantum})"
    def reset(self):
        """Hazır kuyruğunu sıfırlar (her simülasyon başında çağrılır)."""
        self.ready_queue.clear()

    def get_time_quantum(self):
        """Simülatörün kesme kararı için kullandığı zaman dilimini döner."""
        return self.time_quantum

    def add_process(self, process):
        """Yeni gelen (veya kuantumu biten) süreci kuyruğun sonuna ekler."""
        self.ready_queue.add(process)

    def select_next(self, current_time):
        """Kuyruktan sıradaki ilk süreci seçer (FIFO sırasıyla).

        Round Robin'de süreçler geliş sırasına göre işlendiğinden
        her zaman kuyruğun başındaki süreç seçilir.
        """
        if self.ready_queue.is_empty():
            return None
        return self.ready_queue.pop_first()

    def should_preempt(self, running_process, current_time):
        """Round Robin kesmeyi quantum dolduğunda simülatör yapar; bu metod hep False döner.

        Simülatör ``get_time_quantum()`` ile quantum değerini alarak
        dolduğunda süreci kuyruğa geri ekler. Dolayısıyla bu metoda
        gerek yoktur.
        """
        return False


    def should_preempt(self, running_process, current_time):
        """Round Robin kesmeyi quantum dolduğunda simülatör yapar; bu metod hep False döner.

        Simülatör ``get_time_quantum()`` ile quantum değerini alarak
        dolduğunda süreci kuyruğa geri ekler. Dolayısıyla bu metoda
        gerek yoktur.
        """
        return False
