from scheduler import Scheduler


class FCFSScheduler(Scheduler):
    """İlk gelen ilk hizmet alır."""
    name = "FCFS"

    def select_next(self, current_time):
        raise NotImplementedError("FCFS.select_next")