from algorithms import create_all_schedulers
from simulator import Simulator

def run_all(processes, time_quantum=4):
    """Tüm algoritmaları aynı süreç listesiyle çalıştırır ve sonuçları döndürür."""
    simulator = Simulator(processes)
    results = []
    for scheduler in create_all_schedulers(time_quantum):
        results.append(simulator.run(scheduler))
    return results