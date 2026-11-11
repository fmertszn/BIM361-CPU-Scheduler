

import os
import sys
import unittest

# Proje kök dizinini sys.path'e ekle (her dizinden çalıştırılabilmesi için)
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from algorithms.fcfs import FCFSScheduler
from algorithms.priority import PriorityScheduler
from algorithms.round_robin import RoundRobinScheduler
from algorithms.sjf import SJFScheduler
from algorithms.srtf import SRTFScheduler
from analysis import best_algorithm, run_all, sort_results
from gantt import GanttChart
from input_reader import InputValidationError, read_processes
from simulator import Simulator


def data_path(filename):
    """data/ klasöründeki dosyanın tam yolunu döndürür."""
    return os.path.join(ROOT_DIR, "data", filename)


def gantt_tuples(result):
    """Test karşılaştırması için Gantt kayıtlarını (id, başlangıç, bitiş) listesine çevirir."""
    return [(e.process_id, e.start_time, e.end_time) for e in result.gantt_chart.entries]


class TestVeriA(unittest.TestCase):
    """data/veri_a.txt (P1: 0,5,2 | P2: 2,3,1 | P3: 4,1,3) testleri."""

    @classmethod
    def setUpClass(cls):
        cls.processes = read_processes(data_path("veri_a.txt"))
        cls.simulator = Simulator(cls.processes)

    def test_fcfs(self):
        res = self.simulator.run(FCFSScheduler())
        self.assertEqual(gantt_tuples(res), [("P1", 0, 5), ("P2", 5, 8), ("P3", 8, 9)])
        self.assertAlmostEqual(res.avg_waiting_time, 7 / 3)
        self.assertAlmostEqual(res.avg_turnaround_time, 16 / 3)
        self.assertAlmostEqual(res.avg_response_time, 7 / 3)
        self.assertAlmostEqual(res.cpu_utilization, 100.0)

    def test_sjf(self):
        # P1 bittiğinde (t=5) kuyrukta P2(süre=3) ve P3(süre=1) vardır; P3 önce seçilir
        res = self.simulator.run(SJFScheduler())
        self.assertEqual(gantt_tuples(res), [("P1", 0, 5), ("P3", 5, 6), ("P2", 6, 9)])
        self.assertAlmostEqual(res.avg_waiting_time, 5 / 3)
        self.assertAlmostEqual(res.avg_turnaround_time, 14 / 3)
        self.assertAlmostEqual(res.avg_response_time, 5 / 3)

    def test_srtf(self):
        # t=2'de P1'in kalan süresi 3, yeni gelen P2'nin süresi 3 (eşitlikte kesme olmaz)
        # t=4'te P1'in kalan süresi 1, yeni gelen P3'ün süresi 1 (eşitlikte kesme olmaz)
        res = self.simulator.run(SRTFScheduler())
        self.assertEqual(gantt_tuples(res), [("P1", 0, 5), ("P3", 5, 6), ("P2", 6, 9)])
        self.assertAlmostEqual(res.avg_waiting_time, 5 / 3)
        self.assertAlmostEqual(res.avg_turnaround_time, 14 / 3)

    def test_priority_non_preemptive(self):
        # P1 çalışırken kesilmez; t=5'te P2(öncelik=1) P3(öncelik=3)'ten önce seçilir
        res = self.simulator.run(PriorityScheduler(preemptive=False))
        self.assertEqual(gantt_tuples(res), [("P1", 0, 5), ("P2", 5, 8), ("P3", 8, 9)])
        self.assertAlmostEqual(res.avg_waiting_time, 7 / 3)

    def test_priority_preemptive(self):
        # t=2'de P2(öncelik=1) gelir ve P1(öncelik=2)'i keser
        res = self.simulator.run(PriorityScheduler(preemptive=True))
        self.assertEqual(
            gantt_tuples(res),
            [("P1", 0, 2), ("P2", 2, 5), ("P1", 5, 8), ("P3", 8, 9)],
        )
        self.assertAlmostEqual(res.avg_waiting_time, 7 / 3)
        self.assertAlmostEqual(res.avg_turnaround_time, 16 / 3)
        self.assertAlmostEqual(res.avg_response_time, 4 / 3)

    def test_round_robin_q4(self):
        res = self.simulator.run(RoundRobinScheduler(time_quantum=4))
        self.assertEqual(
            gantt_tuples(res),
            [("P1", 0, 4), ("P2", 4, 7), ("P3", 7, 8), ("P1", 8, 9)],
        )
        self.assertAlmostEqual(res.avg_waiting_time, 3.0)
        self.assertAlmostEqual(res.avg_turnaround_time, 6.0)
        self.assertAlmostEqual(res.avg_response_time, 5 / 3)


class TestVeriB(unittest.TestCase):
    """data/veri_b.txt (Silberschatz klasik SRTF örneği) testleri."""

    @classmethod
    def setUpClass(cls):
        cls.processes = read_processes(data_path("veri_b.txt"))
        cls.simulator = Simulator(cls.processes)

    def test_fcfs(self):
        res = self.simulator.run(FCFSScheduler())
        self.assertEqual(
            gantt_tuples(res),
            [("P1", 0, 8), ("P2", 8, 12), ("P3", 12, 21), ("P4", 21, 26)],
        )
        self.assertAlmostEqual(res.avg_waiting_time, 8.75)
        self.assertAlmostEqual(res.avg_turnaround_time, 15.25)
        self.assertAlmostEqual(res.avg_response_time, 8.75)
        self.assertAlmostEqual(res.cpu_utilization, 100.0)

    def test_sjf(self):
        res = self.simulator.run(SJFScheduler())
        self.assertEqual(
            gantt_tuples(res),
            [("P1", 0, 8), ("P2", 8, 12), ("P4", 12, 17), ("P3", 17, 26)],
        )
        self.assertAlmostEqual(res.avg_waiting_time, 7.75)
        self.assertAlmostEqual(res.avg_turnaround_time, 14.25)
        self.assertAlmostEqual(res.avg_response_time, 7.75)

    def test_srtf(self):
        # Ders kitabındaki klasik sonuç: (9 + 0 + 15 + 2) / 4 = 6.50
        res = self.simulator.run(SRTFScheduler())
        self.assertEqual(
            gantt_tuples(res),
            [("P1", 0, 1), ("P2", 1, 5), ("P4", 5, 10), ("P1", 10, 17), ("P3", 17, 26)],
        )
        self.assertAlmostEqual(res.avg_waiting_time, 6.50)
        self.assertAlmostEqual(res.avg_turnaround_time, 13.00)
        self.assertAlmostEqual(res.avg_response_time, 4.25)

        bekleme_sureleri = {p.process_id: p.waiting_time for p in res.processes}
        self.assertEqual(bekleme_sureleri, {"P1": 9, "P2": 0, "P3": 15, "P4": 2})

    def test_priority_non_preemptive(self):
        res = self.simulator.run(PriorityScheduler(preemptive=False))
        self.assertEqual(
            gantt_tuples(res),
            [("P1", 0, 8), ("P2", 8, 12), ("P4", 12, 17), ("P3", 17, 26)],
        )
        self.assertAlmostEqual(res.avg_waiting_time, 7.75)

    def test_priority_preemptive(self):
        res = self.simulator.run(PriorityScheduler(preemptive=True))
        self.assertEqual(
            gantt_tuples(res),
            [("P1", 0, 1), ("P2", 1, 5), ("P4", 5, 10), ("P1", 10, 17), ("P3", 17, 26)],
        )
        self.assertAlmostEqual(res.avg_waiting_time, 6.50)
        self.assertAlmostEqual(res.avg_turnaround_time, 13.00)
        self.assertAlmostEqual(res.avg_response_time, 4.25)

    def test_round_robin_q4(self):
        res = self.simulator.run(RoundRobinScheduler(time_quantum=4))
        self.assertEqual(
            gantt_tuples(res),
            [
                ("P1", 0, 4),
                ("P2", 4, 8),
                ("P3", 8, 12),
                ("P4", 12, 16),
                ("P1", 16, 20),
                ("P3", 20, 24),
                ("P4", 24, 25),
                ("P3", 25, 26),
            ],
        )
        self.assertAlmostEqual(res.avg_waiting_time, 11.75)
        self.assertAlmostEqual(res.avg_turnaround_time, 18.25)
        self.assertAlmostEqual(res.avg_response_time, 4.50)

    def test_best_algorithm_on_veri_b(self):
        results = run_all(self.processes, time_quantum=4)
        best = best_algorithm(results)
        self.assertAlmostEqual(best.avg_waiting_time, 6.50)
        self.assertIn(best.algorithm_name, ("SRTF", "Priority (kesintili)"))


class TestVeriC(unittest.TestCase):
    """data/veri_c.txt (CPU'nun IDLE kaldığı durum: P1: 2,3,1 | P2: 10,2,2) testleri."""

    @classmethod
    def setUpClass(cls):
        cls.processes = read_processes(data_path("veri_c.txt"))

    def test_idle_handling_and_cpu_utilization(self):
        results = run_all(self.processes, time_quantum=4)
        beklenen_gantt = [
            (GanttChart.IDLE, 0, 2),
            ("P1", 2, 5),
            (GanttChart.IDLE, 5, 10),
            ("P2", 10, 12),
        ]
        for res in results:
            with self.subTest(algorithm=res.algorithm_name):
                self.assertEqual(gantt_tuples(res), beklenen_gantt)
                self.assertAlmostEqual(res.avg_waiting_time, 0.0)
                self.assertAlmostEqual(res.avg_turnaround_time, 2.5)
                self.assertAlmostEqual(res.avg_response_time, 0.0)
                # Toplam 12 birimin 5 biriminde CPU dolu: %41.666...
                self.assertAlmostEqual(res.cpu_utilization, (5 / 12) * 100)


class TestVeriD(unittest.TestCase):
    """data/veri_d.txt (Aynı anda geliş ve eşitlik bozma: P1: 0,4,2 | P2: 0,4,2 | P3: 0,2,1) testleri."""

    @classmethod
    def setUpClass(cls):
        cls.processes = read_processes(data_path("veri_d.txt"))
        cls.simulator = Simulator(cls.processes)

    def test_fcfs_and_rr_q4_preserve_arrival_order(self):
        for scheduler in (FCFSScheduler(), RoundRobinScheduler(time_quantum=4)):
            with self.subTest(scheduler=scheduler.name):
                res = self.simulator.run(scheduler)
                self.assertEqual(
                    gantt_tuples(res),
                    [("P1", 0, 4), ("P2", 4, 8), ("P3", 8, 10)],
                )
                self.assertAlmostEqual(res.avg_waiting_time, 4.0)
                self.assertAlmostEqual(res.avg_turnaround_time, 22 / 3)

    def test_sjf_srtf_priority_tie_breaking(self):
        # P3 en kısa süreye (2) ve en yüksek önceliğe (1) sahip olduğu için ilk çalışır.
        # Ardından P1 ve P2 eşit olduğu için dosyadaki sırayla (P1 -> P2) çalışır.
        schedulers = [
            SJFScheduler(),
            SRTFScheduler(),
            PriorityScheduler(preemptive=False),
            PriorityScheduler(preemptive=True),
        ]
        for scheduler in schedulers:
            with self.subTest(scheduler=scheduler.name):
                res = self.simulator.run(scheduler)
                self.assertEqual(
                    gantt_tuples(res),
                    [("P3", 0, 2), ("P1", 2, 6), ("P2", 6, 10)],
                )
                self.assertAlmostEqual(res.avg_waiting_time, 8 / 3)
                self.assertAlmostEqual(res.avg_turnaround_time, 6.0)
                self.assertAlmostEqual(res.avg_response_time, 8 / 3)

    def test_round_robin_q2(self):
        res = self.simulator.run(RoundRobinScheduler(time_quantum=2))
        self.assertEqual(
            gantt_tuples(res),
            [("P1", 0, 2), ("P2", 2, 4), ("P3", 4, 6), ("P1", 6, 8), ("P2", 8, 10)],
        )
        self.assertAlmostEqual(res.avg_waiting_time, 14 / 3)
        self.assertAlmostEqual(res.avg_turnaround_time, 8.0)
        self.assertAlmostEqual(res.avg_response_time, 2.0)


class TestHataDurumlariVeKorunumluluk(unittest.TestCase):
    """data/test_bos.txt, data/test_hatali.txt ve simülatör güvenlik kontrolleri."""

    def test_bos_dosya_hatasi(self):
        with self.assertRaises(InputValidationError):
            read_processes(data_path("test_bos.txt"))

    def test_hatali_dosya_tum_hatalari_yakalar(self):
        with self.assertRaises(InputValidationError) as ctx:
            read_processes(data_path("test_hatali.txt"))
        # test_hatali.txt içinde 3 ayrı hata var (0 burst, tekrar eden ID P1, sayı olmayan 'x')
        self.assertEqual(len(ctx.exception.errors), 3)

    def test_orijinal_surec_listesi_bozulmaz(self):
        processes = read_processes(data_path("veri_b.txt"))
        sim = Simulator(processes)
        sim.run(SRTFScheduler())
        for p in processes:
            self.assertIsNone(p.start_time)
            self.assertIsNone(p.finish_time)
            self.assertEqual(p.remaining_time, p.burst_time)

    def test_gecersiz_parametreler(self):
        with self.assertRaises(ValueError):
            Simulator([])
        with self.assertRaises(ValueError):
            RoundRobinScheduler(time_quantum=0)
        with self.assertRaises(ValueError):
            RoundRobinScheduler(time_quantum=-2)

    def test_sort_results(self):
        processes = read_processes(data_path("veri_b.txt"))
        results = run_all(processes, time_quantum=4)
        sirali = sort_results(results, metric="avg_waiting_time")
        beklemeler = [r.avg_waiting_time for r in sirali]
        self.assertEqual(beklemeler, sorted(beklemeler))


if __name__ == "__main__":
    unittest.main(verbosity=2)

