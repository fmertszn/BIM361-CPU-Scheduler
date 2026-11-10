"""Girdi okuyucu modülü.

Süreç verilerini dosyadan okur, doğrular ve Process nesneleri üretir.

Desteklenen formatlar:
  1) Metin/CSV (varsayılan), her satır:  ID, geliş, süre, öncelik
         P1, 0, 5, 2
         P2, 2, 3, 1
     Boş satırlar ve '#' ile başlayan satırlar yok sayılır.
  2) JSON (.json uzantılı dosyalar): nesne listesi ya da {"processes": [...]}
         [{"process_id": "P1", "arrival_time": 0, "burst_time": 5, "priority": 2}]

Yapılan doğrulamalar:
  - Dosya boş (hiç süreç yok)
  - Burst süresi 0 veya negatif
  - Aynı ID'ye sahip süreçler
  - Eksik alan, sayısal olmayan değer, negatif geliş zamanı
"""

import json
import os

from process import Process


class InputValidationError(ValueError):
    """Girdi doğrulama hatası. Bulunan tüm hataları `errors` listesinde tutar."""

    def __init__(self, errors):
        if isinstance(errors, str):
            errors = [errors]
        self.errors = list(errors)
        super().__init__("\n".join(self.errors))


# JSON'da kabul edilen alternatif alan adları
_ALANLAR = {
    "process_id": ("process_id", "id", "pid"),
    "arrival_time": ("arrival_time", "arrival", "geliş", "gelis"),
    "burst_time": ("burst_time", "burst", "süre", "sure"),
    "priority": ("priority", "öncelik", "oncelik"),
}


def _to_int(value, alan, konum, errors):
    """Değeri tam sayıya çevirir; olmazsa hata ekler ve None döner."""
    if isinstance(value, bool):
        errors.append(f"{konum}: '{alan}' sayı olmalı, bool verilmiş.")
        return None
    if isinstance(value, float):
        if value.is_integer():
            return int(value)
        errors.append(f"{konum}: '{alan}' tam sayı olmalı, '{value}' verilmiş.")
        return None
    try:
        return int(str(value).strip())
    except (ValueError, TypeError):
        errors.append(f"{konum}: '{alan}' tam sayı olmalı, '{value}' verilmiş.")
        return None


def _read_text_records(path):
    """Metin dosyasını (konum, id, geliş, süre, öncelik) kayıtlarına ayırır."""
    kayitlar, errors = [], []
    with open(path, "r", encoding="utf-8-sig") as f:
        for no, satir in enumerate(f, start=1):
            satir = satir.strip()
            if not satir or satir.startswith("#"):
                continue
            parcalar = [p.strip() for p in satir.split(",")]
            konum = f"Satır {no}"
            if len(parcalar) != 4:
                errors.append(
                    f"{konum}: 4 alan bekleniyordu (ID, geliş, süre, öncelik), "
                    f"{len(parcalar)} bulundu: '{satir}'"
                )
                continue
            kayitlar.append((konum, *parcalar))
    return kayitlar, errors


def _read_json_records(path):
    """JSON dosyasını (konum, id, geliş, süre, öncelik) kayıtlarına ayırır."""
    kayitlar, errors = [], []
    with open(path, "r", encoding="utf-8-sig") as f:
        icerik = f.read()

    if not icerik.strip():
        return kayitlar, errors  # boşluk kontrolü üst katmanda yapılır

    try:
        veri = json.loads(icerik)
    except json.JSONDecodeError as e:
        raise InputValidationError(
            f"Geçersiz JSON (satır {e.lineno}, sütun {e.colno}): {e.msg}"
        )

    if isinstance(veri, dict):
        veri = veri.get("processes", veri.get("süreçler", None))
    if not isinstance(veri, list):
        raise InputValidationError(
            "JSON kökü bir süreç listesi ya da {\"processes\": [...]} olmalı."
        )

    for sira, oge in enumerate(veri, start=1):
        konum = f"Kayıt {sira}"
        if not isinstance(oge, dict):
            errors.append(f"{konum}: nesne bekleniyordu, '{oge}' bulundu.")
            continue

        degerler, eksik = [], False
        for alan, takma_adlar in _ALANLAR.items():
            bulunan = next((oge[a] for a in takma_adlar if a in oge), None)
            if bulunan is None:
                errors.append(f"{konum}: '{alan}' alanı eksik.")
                eksik = True
            degerler.append(bulunan)
        if not eksik:
            kayitlar.append((konum, *degerler))
    return kayitlar, errors


def _build_processes(kayitlar, errors):
    """Kayıtları doğrular ve Process nesnelerine çevirir."""
    sureçler, gorulen_idler = [], {}

    for konum, pid, geliş, süre, öncelik in kayitlar:
        pid = str(pid).strip()
        if not pid:
            errors.append(f"{konum}: süreç ID'si boş olamaz.")
            continue

        if pid in gorulen_idler:
            errors.append(
                f"{konum}: '{pid}' ID'si tekrar ediyor "
                f"(ilk tanım: {gorulen_idler[pid]})."
            )
            continue
        gorulen_idler[pid] = konum

        arrival = _to_int(geliş, "arrival_time", konum, errors)
        burst = _to_int(süre, "burst_time", konum, errors)
        priority = _to_int(öncelik, "priority", konum, errors)
        if arrival is None or burst is None or priority is None:
            continue

        if burst <= 0:
            errors.append(
                f"{konum}: '{pid}' için burst süresi 0'dan büyük olmalı, {burst} verilmiş."
            )
            continue
        if arrival < 0:
            errors.append(
                f"{konum}: '{pid}' için geliş zamanı negatif olamaz, {arrival} verilmiş."
            )
            continue

        sureçler.append(Process(pid, arrival, burst, priority))
    return sureçler


def read_processes(path):
    """Dosyadan süreçleri okur ve Process nesneleri listesi döner.

    Hata durumunda tüm hataları toplayıp tek bir InputValidationError fırlatır.
    """
    if not os.path.isfile(path):
        raise InputValidationError(f"Dosya bulunamadı: {path}")

    if os.path.getsize(path) == 0:
        raise InputValidationError(f"Girdi dosyası boş: {path}")

    if path.lower().endswith(".json"):
        kayitlar, errors = _read_json_records(path)
    else:
        kayitlar, errors = _read_text_records(path)

    if not kayitlar and not errors:
        raise InputValidationError(
            f"Dosyada okunabilir süreç yok (yalnızca boş satır/yorum olabilir): {path}"
        )

    sureçler = _build_processes(kayitlar, errors)

    if errors:
        raise InputValidationError(errors)
    return sureçler


if __name__ == "__main__":
    import sys

    dosya = sys.argv[1] if len(sys.argv) > 1 else "processes.txt"
    try:
        for p in read_processes(dosya):
            print(p)
    except InputValidationError as hata:
        print(f"Girdi hatası ({len(hata.errors)} adet):")
        for h in hata.errors:
            print(f"  - {h}")