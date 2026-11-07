from scheduler import Scheduler


class PriorityScheduler(Scheduler):
    """Önceliğe göre işleme alınır."""
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