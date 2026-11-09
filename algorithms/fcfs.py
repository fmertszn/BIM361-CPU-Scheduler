from ready_queue import ReadyQueue
from gantt import GanttChart, GanttEntry
from metrics import calculate_averages


class FCFSScheduler:
    """First-Come, First-Served (FCFS) CPU Zamanlama Algoritması."""

    def __init__(self, processes):
        # Orijinal süreç listesini bozmamak için kopya oluşturuyoruz ve resetliyoruz
        self.processes = [p for p in processes]
        for p in self.processes:
            p.reset()

        self.ready_queue = ReadyQueue()
        self.gantt_chart = GanttChart()

    def run(self):
        """FCFS simülasyonunu çalıştırır."""
        # Süreçleri geliş zamanlarına (arrival_time) göre sıralıyoruz
        # Aynı anda gelenler için process_id sıralaması yapılabilir (stabilite için)
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

            # 2. Eğer CPU boşta ise ve kuyrukta süreç varsa bir sonraki süreci al
            if current_process is None:
                if not self.ready_queue.is_empty():
                    current_process = self.ready_queue.pop_first()

                    # İlk kez çalışmaya başlıyorsa start_time kaydet
                    if current_process.start_time is None:
                        current_process.start_time = current_time

                    # Gantt şeması için çalışma aralığını başlatıyoruz
                    gantt_start = current_time
                else:
                    # Kuyruk boşsa CPU IDLE (boşta) kalır
                    # Zamanı ilerletmek için sonraki sürecin geliş zamanına zıplayabiliriz
                    if un_arrived:
                        next_arrival = un_arrived[0].arrival_time
                        if current_time < next_arrival:
                            # IDLE geçen süreyi Gantt şemasına ekle
                            self.gantt_chart.add_entry(
                                GanttEntry(
                                    GanttChart.IDLE, current_time, next_arrival
                                )
                            )
                            current_time = next_arrival
                            continue
                    current_time += 1
                    continue

            # 3. Sürecin çalıştırılması (Non-preemptive / Kesintisiz FCFS)
            # Kalan süresini burst_time kadar tüketiyoruz (tamamını bitiriyoruz)
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