from gantt import GanttChart


def calculate_averages(result):
    """Bekleme, dönüş ve yanıt sürelerinin ortalamasını hesaplar."""
    processes = result.processes
    n = len(processes)
    
    for p in processes:
        p.turnaround_time = p.finish_time - p.arrival_time
        p.waiting_time = p.turnaround_time - p.burst_time
    
    result.avg_waiting_time = sum(p.waiting_time for p in processes) / n
    result.avg_turnaround_time = sum(p.turnaround_time for p in processes) / n
    result.avg_response_time = sum(p.start_time - p.arrival_time for p in processes) / n
    
    entries = result.gantt_chart.entries
    busy = sum(e.duration() for e in entries if e.process_id != GanttChart.IDLE)
    total = entries[-1].end_time
    result.cpu_utilization = 100 * busy / total
    
