import copy
from gantt import GanttChart

class SimulationResult:
    """Bir algoritmanın sonuçları ve ortalamaları."""
    def __init__(self, algorithm_name, processes, gantt_chart):
        self.algorithm_name = algorithm_name
        self.processes = processes
        self.gantt_chart = gantt_chart

        self.avg_waiting_time = 0.0
        self.avg_turnaround_time = 0.0
        self.avg_response_time = 0.0
        self.cpu_utilization = 0.0


class Simulator:
    """Zamanı ilerleterek algoritmayı çalıştırır."""
    def __init__(self, processes):
        if not processes:
            raise ValueError("En az bir süreç gerekli")
        self.processes = processes

    def run(self, scheduler):
        processes = copy.deepcopy(self.processes)
        for p in processes:
            p.reset()
        scheduler.reset()
        gantt_chart = GanttChart()

        raise NotImplementedError("Simulator.run")

    @staticmethod
    def add_arrivals(processes, scheduler, current_time):
        for p in processes:
            if p.arrival_time == current_time:
                scheduler.add_process(p)

    @staticmethod
    def all_finished(processes):
        return all(p.finish_time is not None for p in processes)
