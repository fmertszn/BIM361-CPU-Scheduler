class Process:
    """Sürecin girdi bilgilerini ve sonuçlari tutan sinif."""
    
    def __init__(self, process_id, arrival_time, burst_time, priority):
        self.process_id = process_id #Sürecin adi
        self.arrival_time = int(arrival_time) #kuyruğa geldiği zaman
        self.burst_time = int(burst_time) #CPU'da çalışma süresi
        self.priority = int(priority) #Öncelik değeri
        
        self.remaining_time = self.burst_time #Kalan süre - başta burst_time ile aynı
        #Henüz çalışmadığı için her ikisi de None
        self.start_time = None 
        self.finish_time = None 
        self.waiting_time = 0 # turnaround_time - burst_time
        self.turnaround_time = 0 #finish_time - arrival_time
        
    def reset(self):
        """Her bir algoritma için süreç değerlerini sifirlar."""
        self.remaining_time = self.burst_time
        self.start_time = None
        self.finish_time = None
        self.waiting_time = 0
        self.turnaround_time = 0
        
    def __str__(self):
        return (f"[{self.process_id} | Geliş: {self.arrival_time} | "
                f"Süre: {self.burst_time} | Öncelik: {self.priority}]") #Nesne yazdırılınca burası çalışır.
        