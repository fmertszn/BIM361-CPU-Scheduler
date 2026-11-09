import copy
from gantt import GanttChart
from metrics import calculate_averages


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

        current_time = 0
        running = None
        quantum_used = 0
        quantum = scheduler.get_time_quantum()

        self.add_arrivals(processes, scheduler, current_time)

        while not self.all_finished(processes) and current_time < 50:

            if running is None:
                running = scheduler.select_next(current_time)
                quantum_used = 0
                if running is not None and running.start_time is None:
                    running.start_time = current_time

            if running is not None:
                running.remaining_time -= 1
                quantum_used += 1
                gantt_chart.add(running.process_id, current_time, current_time + 1)
            else:
                gantt_chart.add(GanttChart.IDLE, current_time, current_time + 1)

            current_time += 1
            self.add_arrivals(processes, scheduler, current_time)

            if running is not None and running.remaining_time == 0:
                running.finish_time = current_time
                running = None
            elif running is not None and quantum is not None and quantum_used == quantum:
                scheduler.add_process(running)
                running = None

        result = SimulationResult(scheduler.name, processes, gantt_chart)
        calculate_averages(result)
        return result

    @staticmethod
    def add_arrivals(processes, scheduler, current_time):
        for p in processes:
            if p.arrival_time == current_time:
                scheduler.add_process(p)

    @staticmethod
    def all_finished(processes):
        return all(p.finish_time is not None for p in processes)
