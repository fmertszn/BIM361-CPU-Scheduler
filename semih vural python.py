import copy
import sys
from collections import deque


class Process:
    def __init__(self, process_id, arrival_time, burst_time, priority):
        self.process_id = process_id
        self.arrival_time = int(arrival_time)
        self.burst_time = int(burst_time)
        self.priority = int(priority)

        self.remaining_time = self.burst_time
        self.start_time = None
        self.finish_time = None
        self.waiting_time = 0
        self.turnaround_time = 0

    def reset(self):
        self.remaining_time = self.burst_time
        self.start_time = None
        self.finish_time = None
        self.waiting_time = 0
        self.turnaround_time = 0

    def __str__(self):
        return (f"[{self.process_id} | Geliş: {self.arrival_time} | "
                f"Süre: {self.burst_time} | Öncelik: {self.priority}]")


def read_processes_from_file(filename):
    process_list = []
    with open(filename, "r", encoding="utf-8") as file:
        for line_no, line in enumerate(file, start=1):
            if not line.strip():
                continue

            data = [x.strip() for x in line.split(",")]

            if len(data) != 4:
                print(
                    f"Error: {line_no}. satır atlandı 4 alan bekleniyordu: {line.strip()}"
                )
                continue

            try:
                process_list.append(Process(*data))
            except ValueError:
                print(f"Error: {line_no}. satırda sayısal değer hatalı: {line.strip()}")

    return process_list


class ReadyQueue:
    def __init__(self):
        self.queue = deque()

    def add(self, process):
        self.queue.append(process)

    def pop_first(self):
        if self.is_empty():
            return None
        return self.queue.popleft()

    def peek_min(self, key):
        if self.is_empty():
            return None
        return min(self.queue, key=key)

    def pop_min(self, key):
        selected = self.peek_min(key)
        if selected is not None:
            self.queue.remove(selected)
        return selected

    def is_empty(self):
        return len(self.queue) == 0

    def clear(self):
        self.queue.clear()

    def __len__(self):
        return len(self.queue)

    def __iter__(self):
        return iter(self.queue)

    def __str__(self):
        if self.is_empty():
            return "Ready Queue: [boş]"
        return "Ready Queue: [" + ", ".join(p.process_id for p in self.queue) + "]"


class GanttEntry:
    def __init__(self, process_id, start_time, end_time):
        self.process_id = process_id
        self.start_time = start_time
        self.end_time = end_time

    def duration(self):
        return self.end_time - self.start_time

    def __str__(self):
        return f"{self.process_id}({self.start_time}-{self.end_time})"


class GanttChart:
    IDLE = "IDLE"

    def __init__(self):
        self.entries = []

    def add(self, process_id, start_time, end_time):
        if end_time <= start_time:
            return
        if self.entries:
            last = self.entries[-1]
            if last.process_id == process_id and last.end_time == start_time:
                last.end_time = end_time
                return
        self.entries.append(GanttEntry(process_id, start_time, end_time))

    def context_switch_count(self):
        running = [e.process_id for e in self.entries if e.process_id != self.IDLE]
        return sum(1 for a, b in zip(running, running[1:]) if a != b)

    def draw(self):
        if not self.entries:
            return "Gantt: [boş]"
        bar = "|"
        times = str(self.entries[0].start_time)
        for entry in self.entries:
            width = max(len(entry.process_id) + 2, entry.duration())
            bar += entry.process_id.center(width) + "|"
            times = times.ljust(len(bar) - 1) + str(entry.end_time)
        return bar + "\n" + times

    def __str__(self):
        return self.draw()


class Scheduler:
    name = "Scheduler"

    def __init__(self):
        self.ready_queue = ReadyQueue()

    def add_process(self, process):
        self.ready_queue.add(process)

    def select_next(self, current_time):
        raise NotImplementedError(f"{self.name}.select_next")

    def should_preempt(self, running_process, current_time):
        return False

    def get_time_quantum(self):
        return None

    def reset(self):
        self.ready_queue.clear()


class FCFSScheduler(Scheduler):
    name = "FCFS"

    def select_next(self, current_time):
        raise NotImplementedError("FCFS.select_next")


class SJFScheduler(Scheduler):
    name = "SJF"

    def select_next(self, current_time):
        raise NotImplementedError("SJF.select_next")


class SRTFScheduler(Scheduler):
    name = "SRTF"

    def select_next(self, current_time):
        raise NotImplementedError("SRTF.select_next")

    def should_preempt(self, running_process, current_time):
        raise NotImplementedError("SRTF.should_preempt")


class PriorityScheduler(Scheduler):
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


class RoundRobinScheduler(Scheduler):
    def __init__(self, time_quantum=4):
        super().__init__()
        if time_quantum <= 0:
            raise ValueError("Quantum pozitif olmalı")
        self.time_quantum = time_quantum
        self.name = f"Round Robin (q={time_quantum})"

    def get_time_quantum(self):
        return self.time_quantum

    def select_next(self, current_time):
        raise NotImplementedError("RoundRobin.select_next")


def create_all_schedulers(time_quantum=4):
    return [
        FCFSScheduler(),
        SJFScheduler(),
        SRTFScheduler(),
        PriorityScheduler(preemptive=False),
        PriorityScheduler(preemptive=True),
        RoundRobinScheduler(time_quantum),
    ]


class SimulationResult:
    def __init__(self, algorithm_name, processes, gantt_chart):
        self.algorithm_name = algorithm_name
        self.processes = processes
        self.gantt_chart = gantt_chart

        self.avg_waiting_time = 0.0
        self.avg_turnaround_time = 0.0
        self.avg_response_time = 0.0
        self.cpu_utilization = 0.0


class Simulator:
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


def calculate_averages(result):
    raise NotImplementedError("calculate_averages")


def print_process_table(result):
    def show(value):
        return "-" if value is None else str(value)

    print(f"{'Süreç':<7}{'Geliş':>6}{'Süre':>6}{'Önc.':>6}"
          f"{'Başl.':>7}{'Bitiş':>7}{'Bekl.':>7}{'Dönüş':>7}")
    print("-" * 53)
    for p in result.processes:
        print(f"{p.process_id:<7}{p.arrival_time:>6}{p.burst_time:>6}{p.priority:>6}"
              f"{show(p.start_time):>7}{show(p.finish_time):>7}"
              f"{p.waiting_time:>7}{p.turnaround_time:>7}")


def print_comparison(results):
    print(f"{'Algoritma':<24}{'Ort.Bekl.':>10}{'Ort.Dönüş':>11}"
          f"{'Ort.Yanıt':>11}{'CPU %':>8}")
    print("-" * 64)
    for r in results:
        print(f"{r.algorithm_name:<24}{r.avg_waiting_time:>10.2f}"
              f"{r.avg_turnaround_time:>11.2f}{r.avg_response_time:>11.2f}"
              f"{r.cpu_utilization:>8.1f}")


def main():
    filename = sys.argv[1] if len(sys.argv) > 1 else "processes.txt"
    try:
        time_quantum = int(sys.argv[2]) if len(sys.argv) > 2 else 4
        if time_quantum <= 0:
            raise ValueError
    except ValueError:
        print("Error: quantum pozitif bir tam sayı olmalı.")
        return

    try:
        processes = read_processes_from_file(filename)
    except FileNotFoundError:
        print(f"Error: {filename} dosyası bulunamadı.")
        return

    if not processes:
        print("Error: dosyada geçerli süreç bulunamadı.")
        return

    print("Processler başarıyla okundu:\n")
    for p in processes:
        print(p)
    print()

    simulator = Simulator(processes)
    results = []
    for scheduler in create_all_schedulers(time_quantum):
        try:
            result = simulator.run(scheduler)
        except NotImplementedError:
            print(f"[{scheduler.name}] henüz yazılmadı (TODO)")
            continue
        results.append(result)
        print(f"\n=== {result.algorithm_name} ===")
        print(result.gantt_chart)
        print_process_table(result)

    if results:
        print()
        print_comparison(results)


if __name__ == "__main__":
    main()
