from process import Process
import sys
from algorithms import create_all_schedulers
from simulator import Simulator


def read_processes_from_file(filename):
    """Dosyadan processleri okur ve Process listesi döndürür."""
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
