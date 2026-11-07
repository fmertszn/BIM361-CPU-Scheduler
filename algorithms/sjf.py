from scheduler import Scheduler


class SJFScheduler(Scheduler):
    """En kısa işleme öncelik verilir."""
    name = "SJF"

    def select_next(self, current_time):
        raise NotImplementedError("SJF.select_next")