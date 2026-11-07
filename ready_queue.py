from collections import deque


class ReadyQueue:
    """CPU’yu bekleyen süreçlerin hazır kuyruğu."""
    def __init__(self):
        self.queue = deque()

    def add(self, process):
        self.queue.append(process)

    def pop_first(self):
        if self.is_empty():
            return None
        return self.queue.popleft()

    def peek_min(self, key):
        if self.is_empty():
            return None
        return min(self.queue, key=key)

    def pop_min(self, key):
        selected = self.peek_min(key)
        if selected is not None:
            self.queue.remove(selected)
        return selected

    def is_empty(self):
        return len(self.queue) == 0

    def clear(self):
        self.queue.clear()

    def __len__(self):
        return len(self.queue)

    def __iter__(self):
        return iter(self.queue)

    def __str__(self):
        if self.is_empty():
            return "Ready Queue: [boş]"
        return "Ready Queue: [" + ", ".join(p.process_id for p in self.queue) + "]"