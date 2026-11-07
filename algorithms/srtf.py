from scheduler import Scheduler


class SRTFScheduler(Scheduler):
    """En kısa kalan işleme öncelik verilir."""
    name = "SRTF"

    def select_next(self, current_time):
        raise NotImplementedError("SRTF.select_next")

    def should_preempt(self, running_process, current_time):
        raise NotImplementedError("SRTF.should_preempt")
