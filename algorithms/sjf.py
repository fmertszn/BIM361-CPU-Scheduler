from ready_queue import ReadyQueue
from gantt import GanttChart, GanttEntry
from metrics import calculate_averages


class SJFScheduler:
    """Shortest Job First (SJF - Non-Preemptive) CPU Zamanlama Algoritması."""

    def __init__(self, processes):
        # Orijinal süreç listesini bozmamak için kopya oluşturuyoruz ve resetliyoruz
        self.processes = [p for p in processes]
        for p in self.processes:
            p.reset()

        self.ready_queue = ReadyQueue()
        self.gantt_chart = GanttChart()

    def run(self):
        """SJF (Non-Preemptive) simülasyonunu çalıştırır."""
        # Süreçleri geliş zamanlarına göre sıralıyoruz
        un_arrived = sorted(
            self.processes, key=lambda p: (p.arrival_time, p.process_id)
        )

        current_time = 0
        completed_count = 0
        n = len(self.processes)

        current_process = None

        while completed_count < n:
            # 1. Yeni gelen süreçleri hazır kuyruğuna (ready_queue) ekle
            while un_arrived and un_arrived[0].arrival_time <= current_time:
                self.ready_queue.add(un_arrived.pop(0))

            # 2. Eğer CPU boşta ise ve kuyrukta süreç varsa burst_time'ı en kısa olanı seç
            if current_process is None:
                if not self.ready_queue.is_empty():
                    # ReadyQueue içerisindeki pop_min fonksiyonunu burst_time'a göre çağırıyoruz.
                    # Eşitlik durumunda arrival_time ve process_id'ye bakarak kararlı (stable) seçim yapıyoruz.
                    current_process = self.ready_queue.pop_min(
                        key=lambda p: (p.burst_time, p.arrival_time, p.process_id)
                    )

                    # İlk kez çalışmaya başlıyorsa start_time kaydet
                    if current_process.start_time is None:
                        current_process.start_time = current_time
                else:
                    # Kuyruk boşsa CPU IDLE (boşta) kalır, sonraki sürecin gelişine zıpla
                    if un_arrived:
                        next_arrival = un_arrived[0].arrival_time
                        if current_time < next_arrival:
                            self.gantt_chart.add_entry(
                                GanttEntry(
                                    GanttChart.IDLE, current_time, next_arrival
                                )
                            )
                            current_time = next_arrival
                            continue
                    current_time += 1
                    continue

            # 3. Sürecin Kesintisiz (Non-Preemptive) Çalıştırılması
            execution_duration = current_process.remaining_time
            start_exec_time = current_time
            current_time += execution_duration

            current_process.remaining_time = 0
            current_process.finish_time = current_time

            # Gantt şemasına bu sürecin çalışma aralığını ekle
            self.gantt_chart.add_entry(
                GanttEntry(
                    current_process.process_id,
                    start_exec_time,
                    current_time,
                )
            )

            completed_count += 1
            current_process = None  # CPU tekrar boş duruma geçiyor

        # Simülasyon bittiğinde metrics.py'deki calculate_averages fonksiyonunu çağırıyoruz
        class ResultWrapper:
            pass

        result = ResultWrapper()
        result.processes = self.processes
        result.gantt_chart = self.gantt_chart

        calculate_averages(result)

        return {
            "processes": self.processes,
            "gantt_chart": self.gantt_chart,
            "avg_waiting_time": result.avg_waiting_time,
            "avg_turnaround_time": result.avg_turnaround_time,
            "avg_response_time": result.avg_response_time,
            "cpu_utilization": result.cpu_utilization,
        }