import csv
from algorithms import create_all_schedulers
from simulator import Simulator

def run_all(processes, time_quantum=4):
    """Tüm algoritmaları aynı süreç listesiyle çalıştırır ve sonuçları döndürür."""
    simulator = Simulator(processes)
    results = []
    for scheduler in create_all_schedulers(time_quantum):
        results.append(simulator.run(scheduler))
    return results

def sort_results(results, metric="avg_waiting_time"):
    """Sonuçları verilen metrikle sıralar."""
    return sorted(results, key=lambda r: getattr(r, metric))

def best_algorithm(results, metric="avg_waiting_time"):
    """Seçilen ortalaması en düşük algoritmayı döndürür."""
    return sort_results(results, metric)[0]

def save_results_csv(results, filename):
    """Sonuçları CSV dosyasına kaydeder."""
    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Algoritma", "Ort.Bekl.", "Ort.Dönüş", "Ort.Yanıt", "CPU %"])
        for r in results:
            writer.writerow([
                r.algorithm_name,
                round(r.avg_waiting_time, 2),
                round(r.avg_turnaround_time, 2),
                round(r.avg_response_time, 2),
                round(r.cpu_utilization, 1),
            ])