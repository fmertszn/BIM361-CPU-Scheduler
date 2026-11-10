"""Rastgele süreç üreteci modülü (seed destekli).

Tekrarlanabilir deneyler için sabit bir tohum (seed) değeriyle veya tamamen
rastgele olarak Process nesneleri üretir; istenirse metin (.txt/.csv) ya da
JSON (.json) formatında dosyaya kaydeder.

Örnek kullanım (modül olarak):
    from generator import generate_processes, save_processes
    processes = generate_processes(count=5, seed=42)
    save_processes(processes, "data/rastgele.txt")

Örnek kullanım (komut satırından):
    python generator.py -n 6 -s 42 -o data/rastgele.txt
    python generator.py -n 5 -s 100 --run
"""

import argparse
import json
import random

from process import Process


def generate_processes(
    count=5,
    seed=None,
    arrival_range=(0, 10),
    burst_range=(1, 10),
    priority_range=(1, 5),
    sort_by_arrival=True,
    zero_first_arrival=True,
):
    """Belirtilen aralıklarla rastgele süreç listesi üretir.

    Parametreler:
        count (int): Üretilecek süreç sayısı (>= 1).
        seed (int | None): Tekrarlanabilirlik için rastgelelik tohumu.
        arrival_range (tuple[int, int]): (min, max) geliş zamanı aralığı (>= 0).
        burst_range (tuple[int, int]): (min, max) CPU çalışma süresi aralığı (>= 1).
        priority_range (tuple[int, int]): (min, max) öncelik aralığı.
        sort_by_arrival (bool): True ise süreçler geliş zamanına göre sıralanıp
            P1..Pn olarak numaralandırılır.
        zero_first_arrival (bool): True ise ilk sürecin geliş zamanı 0 yapılır.

    Dönüş:
        list[Process]: Üretilen Process nesneleri listesi.
    """
    if count < 1:
        raise ValueError(f"Süreç sayısı en az 1 olmalı, {count} verildi.")

    arr_min, arr_max = arrival_range
    burst_min, burst_max = burst_range
    prio_min, prio_max = priority_range

    if arr_min < 0 or arr_min > arr_max:
        raise ValueError(f"Geçersiz geliş zamanı aralığı: {arrival_range}")
    if burst_min < 1 or burst_min > burst_max:
        raise ValueError(f"Geçersiz çalışma süresi aralığı: {burst_range}")
    if prio_min > prio_max:
        raise ValueError(f"Geçersiz öncelik aralığı: {priority_range}")

    rng = random.Random(seed)

    ham_degerler = []
    for i in range(count):
        arrival = rng.randint(arr_min, arr_max)
        burst = rng.randint(burst_min, burst_max)
        priority = rng.randint(prio_min, prio_max)
        ham_degerler.append([arrival, burst, priority])

    if zero_first_arrival and ham_degerler and arr_min == 0:
        ham_degerler[0][0] = 0

    if sort_by_arrival:
        ham_degerler.sort(key=lambda item: item[0])

    processes = [
        Process(f"P{sira}", arrival, burst, priority)
        for sira, (arrival, burst, priority) in enumerate(ham_degerler, start=1)
    ]
    return processes


def save_processes_txt(processes, path):
    """Süreç listesini 'ID, geliş, süre, öncelik' metin formatında kaydeder."""
    with open(path, "w", encoding="utf-8") as f:
        for p in processes:
            f.write(f"{p.process_id}, {p.arrival_time}, {p.burst_time}, {p.priority}\n")


def save_processes_json(processes, path):
    """Süreç listesini input_reader.py ile uyumlu JSON formatında kaydeder."""
    veri = [
        {
            "process_id": p.process_id,
            "arrival_time": p.arrival_time,
            "burst_time": p.burst_time,
            "priority": p.priority,
        }
        for p in processes
    ]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(veri, f, ensure_ascii=False, indent=2)
        f.write("\n")


def save_processes(processes, path):
    """Dosya uzantısına göre (.json veya metin) süreçleri kaydeder."""
    if path.lower().endswith(".json"):
        save_processes_json(processes, path)
    else:
        save_processes_txt(processes, path)


def _build_arg_parser():
    parser = argparse.ArgumentParser(
        description="Seed destekli rastgele süreç (process) üreteci."
    )
    parser.add_argument(
        "-n", "--count", type=int, default=5, help="Üretilecek süreç sayısı (varsayılan: 5)"
    )
    parser.add_argument(
        "-s", "--seed", type=int, default=None, help="Rastgelelik tohumu (seed)"
    )
    parser.add_argument(
        "--arrival-min", type=int, default=0, help="En erken geliş zamanı (varsayılan: 0)"
    )
    parser.add_argument(
        "--arrival-max", type=int, default=10, help="En geç geliş zamanı (varsayılan: 10)"
    )
    parser.add_argument(
        "--burst-min", type=int, default=1, help="En kısa CPU süresi (varsayılan: 1)"
    )
    parser.add_argument(
        "--burst-max", type=int, default=10, help="En uzun CPU süresi (varsayılan: 10)"
    )
    parser.add_argument(
        "--priority-min", type=int, default=1, help="En yüksek öncelik sayısı (varsayılan: 1)"
    )
    parser.add_argument(
        "--priority-max", type=int, default=5, help="En düşük öncelik sayısı (varsayılan: 5)"
    )
    parser.add_argument(
        "--no-zero-first",
        action="store_true",
        help="İlk sürecin geliş zamanını 0'a sabitleme",
    )
    parser.add_argument(
        "-o", "--output", type=str, default=None, help="Kaydedilecek dosya yolu (.txt veya .json)"
    )
    parser.add_argument(
        "--run",
        action="store_true",
        help="Üretilen süreçlerle simülasyonu hemen çalıştır",
    )
    parser.add_argument(
        "-q", "--quantum", type=int, default=4, help="Round Robin quantum değeri (varsayılan: 4)"
    )
    return parser


def main():
    parser = _build_arg_parser()
    args = parser.parse_args()

    try:
        processes = generate_processes(
            count=args.count,
            seed=args.seed,
            arrival_range=(args.arrival_min, args.arrival_max),
            burst_range=(args.burst_min, args.burst_max),
            priority_range=(args.priority_min, args.priority_max),
            zero_first_arrival=not args.no_zero_first,
        )
    except ValueError as e:
        print(f"Error: {e}")
        return

    seed_bilgi = f" (seed={args.seed})" if args.seed is not None else " (rastgele)"
    print(f"Üretilen süreçler ({len(processes)} adet){seed_bilgi}:\n")
    for p in processes:
        print(f"  {p.process_id}, {p.arrival_time}, {p.burst_time}, {p.priority}   ->  {p}")

    if args.output:
        save_processes(processes, args.output)
        print(f"\nSüreçler kaydedildi: {args.output}")

    if args.run:
        from analysis import best_algorithm, run_all
        from main import print_comparison, print_process_table

        results = run_all(processes, args.quantum)
        for result in results:
            print(f"\n=== {result.algorithm_name} ===")
            print(result.gantt_chart)
            print_process_table(result)
        print()
        print_comparison(results)
        best = best_algorithm(results)
        print(
            f"\nEn düşük ortalama bekleme süresi: "
            f"{best.algorithm_name} ({best.avg_waiting_time:.2f})"
        )


if __name__ == "__main__":
    main()

