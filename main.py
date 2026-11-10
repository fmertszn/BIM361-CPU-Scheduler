import sys
from analysis import run_all, best_algorithm, save_results_csv
from input_reader import read_processes, InputValidationError

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
        processes = read_processes(filename)
    except InputValidationError as e:
        print(f"Error: {filename} dosyasında {len(e.errors)} girdi hatası var:")
        for hata in e.errors:
            print(f"  - {hata}")
        return

    print("Processler başarıyla okundu:\n")
    for p in processes:
        print(p)
    print()

    results = run_all(processes, time_quantum)
    for result in results:
        print(f"\n=== {result.algorithm_name} ===")
        print(result.gantt_chart)
        print_process_table(result)
    
    print()
    print_comparison(results)
    
    best = best_algorithm(results)
    print(f"\nEn düşük ortalama bekleme süresi: {best.algorithm_name} ({best.avg_waiting_time:.2f})")

    if len(sys.argv) > 3:
        save_results_csv(results, sys.argv[3])
        print(f"Sonuçlar kaydedildi: {sys.argv[3]}")

if __name__ == "__main__":
    main()
