from process import Process


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


if __name__ == "__main__":
    try:
        processes = read_processes_from_file("processes.txt")
    except FileNotFoundError:
        print("Error: processes.txt dosyası bulunamadı.")
    else:
        print("Processler başarıyla okundu:\n")
        for p in processes:
            print(p)
