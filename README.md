# BİM361 - CPU Zamanlama Simülatörü

BİM361 İşletim Sistemleri dersi dönem projesi. FCFS, SJF, SRTF, Round Robin ve Priority algoritmalarını aynı süreç listesi üzerinde çalıştırıp Gantt şeması, ortalama bekleme, dönüş ve yanıt süreleriyle karşılaştırır.

Referans: Silberschatz, Operating System Concepts, Bölüm 5.

## Çalıştırma

Python 3 yeterli, ek kütüphane gerekmiyor.

```bash
git clone https://github.com/fmertszn/BIM361-CPU-Scheduler.git
cd BIM361-CPU-Scheduler
python main.py
```

Parametreler sırasıyla girdi dosyası, Round Robin quantum değeri ve isteğe bağlı CSV çıktısıdır. Hiçbiri verilmezse `processes.txt` ve quantum 4 kullanılır.

```bash
python main.py data/veri_b.txt 4
python main.py data/veri_b.txt 2 sonuc.csv
```

## Girdi

Her satırda bir süreç: ad, geliş zamanı, çalışma süresi, öncelik.

```
P1, 0, 8, 3
P2, 1, 4, 1
P3, 2, 9, 4
P4, 3, 5, 2
```

`data/` klasöründe dört örnek veri var. `veri_b.txt` ders kitabındaki klasik SRTF örneği, `veri_c.txt` CPU'nun boşta kaldığı bir durum, `veri_d.txt` aynı anda gelen süreçler için.

## Çıktı

Her algoritma için Gantt şeması ve süreç bazında başlama, bitiş, bekleme, dönüş süreleri yazdırılır. En sonda tüm algoritmalar tek tabloda karşılaştırılır ve ortalama bekleme süresi en düşük olan algoritma belirtilir.

```
Algoritma                Ort.Bekl.  Ort.Dönüş  Ort.Yanıt   CPU %
----------------------------------------------------------------
FCFS                          8.75      15.25       8.75   100.0
SJF                           7.75      14.25       7.75   100.0
SRTF                          6.50      13.00       4.25   100.0
...
```

## Nasıl çalışıyor

Zamanı ilerleten döngü `Simulator` sınıfında. Algoritmalar sadece CPU boşaldığında sıradaki süreci seçiyor (`select_next`), kesintili olanlar ayrıca çalışan sürecin kesilip kesilmeyeceğine karar veriyor (`should_preempt`). Hepsi `Scheduler` temel sınıfından türüyor. Bu yüzden her algoritma dosyası birkaç satırdan ibaret ve sonuçlar aynı motor üzerinden hesaplandığı için birbiriyle adil karşılaştırılabiliyor.

Simülasyonda uyguladığımız kurallar:

- Aynı anda gelen veya seçimde eşit olan süreçlerde dosyadaki sıra belirleyici.
- SRTF ve kesintili Priority'de çalışan süreç ancak kuyruktaki biri kesin olarak daha iyiyse kesilir, eşitlikte kesilmez.
- Round Robin'de quantum'u biten süreç ile yeni gelen süreç aynı anda kuyruğa girecekse yeni gelen önce girer.
- Priority'de küçük sayı yüksek öncelik demek.

## Dosyalar

- `main.py`: giriş noktası, dosya okuma ve çıktı tabloları
- `process.py`: süreç sınıfı
- `ready_queue.py`: hazır kuyruk
- `gantt.py`: Gantt kaydı ve metin olarak çizimi
- `scheduler.py`: algoritmaların ortak temel sınıfı
- `algorithms/`: her algoritma için ayrı dosya
- `simulator.py`: zaman döngüsü, kesme ve quantum mantığı
- `metrics.py`: bekleme, dönüş, yanıt süresi ve CPU kullanımı hesabı
- `analysis.py`: algoritmaları karşılaştırma, sıralama, CSV kaydı
- `data/`: örnek süreç dosyaları

## Yapılacaklar

JSON girdi, rastgele süreç üreteci, matplotlib ile Gantt grafiği ve otomatik testler üzerinde çalışılıyor.