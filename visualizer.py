"""Matplotlib ile Gantt şeması ve performans metrikleri görselleştirici.

Hem tek bir algoritmanın Gantt şemasını hem de tüm algoritmaların alt alta
karşılaştırmalı Gantt şemalarını ve ortalama metrik grafiklerini çizer.

Örnek kullanım (modül olarak):
    from analysis import run_all
    from input_reader import read_processes
    from visualizer import plot_all_gantts, plot_metrics_comparison

    processes = read_processes("data/veri_b.txt")
    results = run_all(processes, time_quantum=4)
    plot_all_gantts(results, save_path="gantt.png", show=False)

Örnek kullanım (komut satırından):
    python visualizer.py data/veri_b.txt -q 4 -o gantt.png
    python visualizer.py --random 5 --seed 42 -o gantt_seed42.png
"""

import argparse
from gantt import GanttChart


# Süreçler için ayırt edici, okunaklı renk paleti
_RENK_PALETI = [
    "#4C78A8",  # Mavi
    "#F58518",  # Turuncu
    "#54A24B",  # Yeşil
    "#E45756",  # Kırmızı
    "#B279A2",  # Mor
    "#FF9DA6",  # Pembe
    "#9D755D",  # Kahverengi
    "#72B7B2",  # Turkuaz
    "#EECA3B",  # Sarı
    "#BAB0AC",  # Açık gri
]
_IDLE_RENK = "#E0E0E0"


def _require_matplotlib():
    """Matplotlib yüklü değilse anlaşılır bir hata fırlatır."""
    try:
        import matplotlib.pyplot as plt
        import matplotlib.patches as mpatches
        return plt, mpatches
    except ImportError as exc:
        raise RuntimeError(
            "Görselleştirme için 'matplotlib' kütüphanesi gereklidir. "
            "Kurmak için: pip install matplotlib"
        ) from exc


def _build_color_map(entries):
    """Süreç kimliklerine tutarlı renkler atar."""
    renkler = {GanttChart.IDLE: _IDLE_RENK}
    pids = []
    for entry in entries:
        if entry.process_id != GanttChart.IDLE and entry.process_id not in pids:
            pids.append(entry.process_id)
    for idx, pid in enumerate(sorted(pids, key=lambda x: (len(x), x))):
        renkler[pid] = _RENK_PALETI[idx % len(_RENK_PALETI)]
    return renkler


def _extract_gantt_and_title(hedef, title=None):
    """SimulationResult veya GanttChart nesnesinden (gantt, başlık, özet) döner."""
    if hasattr(hedef, "gantt_chart"):
        gantt = hedef.gantt_chart
        varsayilan_baslik = hedef.algorithm_name
        ozet = (
            f"Ort.Bekl: {hedef.avg_waiting_time:.2f} | "
            f"Ort.Dönüş: {hedef.avg_turnaround_time:.2f} | "
            f"Ort.Yanıt: {hedef.avg_response_time:.2f} | "
            f"CPU: %{hedef.cpu_utilization:.1f}"
        )
    elif isinstance(hedef, GanttChart):
        gantt = hedef
        varsayilan_baslik = "Gantt Şeması"
        ozet = None
    else:
        raise TypeError("plot_gantt için SimulationResult veya GanttChart verilmelidir.")

    return gantt, (title or varsayilan_baslik), ozet


def _draw_gantt_on_axis(ax, gantt, renkler, baslik, ozet=None):
    """Verilen matplotlib ekseni (ax) üzerine tek bir Gantt şeması çizer."""
    entries = gantt.entries
    if not entries:
        ax.text(0.5, 0.5, "Gantt: [boş]", ha="center", va="center")
        ax.set_axis_off()
        return

    bar_alt = 0.2
    bar_yukseklik = 0.6

    sinir_zamanlari = {entries[0].start_time}
    for entry in entries:
        sure = entry.duration()
        pid = entry.process_id
        renk = renkler.get(pid, "#4C78A8")
        is_idle = pid == GanttChart.IDLE

        ax.broken_barh(
            [(entry.start_time, sure)],
            (bar_alt, bar_yukseklik),
            facecolors=renk,
            edgecolors="#333333",
            linewidth=1.2,
            hatch="//" if is_idle else None,
            alpha=0.65 if is_idle else 0.92,
        )

        etiket = "BOŞ" if is_idle else pid
        orta_x = entry.start_time + sure / 2.0
        yazi_rengi = "#555555" if is_idle else "white"
        ax.text(
            orta_x,
            bar_alt + bar_yukseklik / 2.0,
            etiket,
            ha="center",
            va="center",
            color=yazi_rengi,
            fontweight="bold",
            fontsize=9,
        )
        sinir_zamanlari.add(entry.end_time)

    toplam_sure = entries[-1].end_time
    ax.set_xlim(entries[0].start_time, max(toplam_sure, 1))
    ax.set_ylim(0, 1.0)
    ax.set_yticks([])

    ticks = sorted(sinir_zamanlari)
    ax.set_xticks(ticks)
    ax.grid(axis="x", linestyle="--", alpha=0.4)

    tam_baslik = f"{baslik}   ({ozet})" if ozet else baslik
    ax.set_title(tam_baslik, fontsize=10, fontweight="bold", loc="left", pad=6)


def plot_gantt(result_or_gantt, title=None, save_path=None, show=True):
    """Tek bir algoritmanın Gantt şemasını matplotlib ile çizer."""
    plt, _ = _require_matplotlib()
    gantt, baslik, ozet = _extract_gantt_and_title(result_or_gantt, title)
    renkler = _build_color_map(gantt.entries)

    fig, ax = plt.subplots(figsize=(10, 2.4))
    _draw_gantt_on_axis(ax, gantt, renkler, baslik, ozet)
    ax.set_xlabel("Zaman (birim)")
    fig.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
    if show:
        plt.show()
    else:
        plt.close(fig)
    return fig


def plot_all_gantts(results, save_path=None, show=True):
    """Tüm algoritmaların Gantt şemalarını tek figürde alt alta karşılaştırır."""
    if not results:
        raise ValueError("Görselleştirilecek sonuç listesi boş.")

    plt, mpatches = _require_matplotlib()

    tum_entries = [e for r in results for e in r.gantt_chart.entries]
    renkler = _build_color_map(tum_entries)

    n = len(results)
    fig, axes = plt.subplots(n, 1, figsize=(11, max(2.0 * n, 3.0)), sharex=False)
    if n == 1:
        axes = [axes]

    max_bitis = max(
        (r.gantt_chart.entries[-1].end_time for r in results if r.gantt_chart.entries),
        default=1,
    )

    for ax, res in zip(axes, results):
        gantt, baslik, ozet = _extract_gantt_and_title(res)
        _draw_gantt_on_axis(ax, gantt, renkler, baslik, ozet)
        ax.set_xlim(0, max_bitis)

    axes[-1].set_xlabel("Zaman (birim)", fontsize=10)

    # Üstte süreç renk anahtarı (legend)
    yamalar = [
        mpatches.Patch(color=renk, label=("IDLE (Boş)" if pid == GanttChart.IDLE else pid))
        for pid, renk in renkler.items()
        if pid != GanttChart.IDLE or any(e.process_id == GanttChart.IDLE for e in tum_entries)
    ]
    if yamalar:
        fig.legend(
            handles=yamalar,
            loc="upper right",
            ncol=min(len(yamalar), 6),
            frameon=True,
            fontsize=9,
        )

    fig.suptitle(
        "CPU Zamanlama Algoritmaları — Gantt Şeması Karşılaştırması",
        fontsize=12,
        fontweight="bold",
        y=0.995,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.96])

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
    if show:
        plt.show()
    else:
        plt.close(fig)
    return fig


def plot_metrics_comparison(results, save_path=None, show=True):
    """Algoritmaların ortalama bekleme, dönüş ve yanıt sürelerini sütun grafiğiyle çizer."""
    if not results:
        raise ValueError("Görselleştirilecek sonuç listesi boş.")

    plt, _ = _require_matplotlib()

    isimler = [r.algorithm_name for r in results]
    bekleme = [r.avg_waiting_time for r in results]
    donus = [r.avg_turnaround_time for r in results]
    yanit = [r.avg_response_time for r in results]

    x = list(range(len(isimler)))
    genislik = 0.25

    fig, ax = plt.subplots(figsize=(10, 5))
    b1 = ax.bar(
        [i - genislik for i in x], bekleme, width=genislik, label="Ort. Bekleme", color="#4C78A8"
    )
    b2 = ax.bar(x, donus, width=genislik, label="Ort. Dönüş", color="#F58518")
    b3 = ax.bar(
        [i + genislik for i in x], yanit, width=genislik, label="Ort. Yanıt", color="#54A24B"
    )

    for grup in (b1, b2, b3):
        for bar in grup:
            yukseklik = bar.get_height()
            ax.annotate(
                f"{yukseklik:.2f}",
                xy=(bar.get_x() + bar.get_width() / 2, yukseklik),
                xytext=(0, 3),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=8,
            )

    ax.set_xticks(x)
    ax.set_xticklabels(isimler, rotation=15, ha="right")
    ax.set_ylabel("Süre (birim)")
    ax.set_title("Algoritma Performans Metrikleri Karşılaştırması", fontweight="bold")
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.legend()
    fig.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
    if show:
        plt.show()
    else:
        plt.close(fig)
    return fig


def _build_arg_parser():
    parser = argparse.ArgumentParser(
        description="CPU zamanlama simülasyonu sonuçlarını matplotlib ile görselleştirir."
    )
    parser.add_argument(
        "input",
        nargs="?",
        default="processes.txt",
        help="Süreç girdi dosyası (varsayılan: processes.txt)",
    )
    parser.add_argument(
        "-q", "--quantum", type=int, default=4, help="Round Robin quantum süresi (varsayılan: 4)"
    )
    parser.add_argument(
        "--random",
        type=int,
        default=None,
        metavar="N",
        help="Dosya yerine N adet rastgele süreç üret",
    )
    parser.add_argument(
        "-s", "--seed", type=int, default=None, help="Rastgele üretim için tohum (seed) değeri"
    )
    parser.add_argument(
        "-o", "--output", type=str, default=None, help="Gantt grafiğini dosyaya kaydet (örn: gantt.png)"
    )
    parser.add_argument(
        "--metrics-output",
        type=str,
        default=None,
        help="Metrik karşılaştırma grafiğini dosyaya kaydet (örn: metrikler.png)",
    )
    parser.add_argument(
        "--no-show",
        action="store_true",
        help="Grafik penceresini açma (yalnızca dosyaya kaydetmek için)",
    )
    return parser


def main():
    from analysis import run_all
    from generator import generate_processes
    from input_reader import InputValidationError, read_processes

    parser = _build_arg_parser()
    args = parser.parse_args()

    if args.random is not None:
        processes = generate_processes(count=args.random, seed=args.seed)
    else:
        try:
            processes = read_processes(args.input)
        except InputValidationError as e:
            print(f"Error: {e}")
            return

    results = run_all(processes, time_quantum=args.quantum)
    show = not args.no_show

    try:
        plot_all_gantts(results, save_path=args.output, show=show)
        if args.output:
            print(f"Gantt grafiği kaydedildi: {args.output}")

        if args.metrics_output:
            plot_metrics_comparison(results, save_path=args.metrics_output, show=show)
            print(f"Metrik grafiği kaydedildi: {args.metrics_output}")
    except RuntimeError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()

