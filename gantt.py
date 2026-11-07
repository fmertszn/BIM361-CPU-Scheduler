class GanttEntry:
    """Tek bir zaman dilimi (hangi süreç, hangi aralıkta)."""
    def __init__(self, process_id, start_time, end_time):
        self.process_id = process_id
        self.start_time = start_time
        self.end_time = end_time

    def duration(self):
        return self.end_time - self.start_time

    def __str__(self):
        return f"{self.process_id}({self.start_time}-{self.end_time})"


class GanttChart:
    """Zaman dilimlerinin listesi, kaydeder ve metin olarak çizer."""
    IDLE = "IDLE"

    def __init__(self):
        self.entries = []

    def add(self, process_id, start_time, end_time):
        if end_time <= start_time:
            return
        if self.entries:
            last = self.entries[-1]
            if last.process_id == process_id and last.end_time == start_time:
                last.end_time = end_time
                return
        self.entries.append(GanttEntry(process_id, start_time, end_time))

    def context_switch_count(self):
        running = [e.process_id for e in self.entries if e.process_id != self.IDLE]
        return sum(1 for a, b in zip(running, running[1:]) if a != b)

    def draw(self):
        if not self.entries:
            return "Gantt: [boş]"
        bar = "|"
        times = str(self.entries[0].start_time)
        for entry in self.entries:
            width = max(len(entry.process_id) + 2, entry.duration())
            bar += entry.process_id.center(width) + "|"
            times = times.ljust(len(bar) - 1) + str(entry.end_time)
        return bar + "\n" + times

    def __str__(self):
        return self.draw()