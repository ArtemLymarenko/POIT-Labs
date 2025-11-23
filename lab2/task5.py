from mpi4py import MPI

def odd(number):
    return number % 2 != 0

def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()
    name = MPI.Get_processor_name()

    # Перевірка на парність кількості процесів
    if size < 2 or odd(size):
        if rank == 0:
            print("Error: Please run with an even number of processes.")
        return

    # Визначаємо сусіда (партнера по обміну)
    neighbor = rank - 1 if odd(rank) else rank + 1

    # === 1. СТВОРЕННЯ СПИСКУ ДАНИХ ===
    # Створимо список, що містить різні типи даних:
    # [номер_процесу, математичне значення, рядок тексту]
    my_list = [rank, rank * 7, f"Hello from P{rank}"]

    print(f"[Process {rank}] Created list: {my_list}")

    # === 2. ПАРНИЙ ОБМІН СПИСКАМИ ===
    # Використовуємо блокуючий обмін (send/recv) для Python-об'єктів

    if odd(rank):
        # Непарний: Відправляє -> Приймає
        comm.send(my_list, dest=neighbor, tag=50)
        received_list = comm.recv(source=neighbor, tag=50)
    else:
        # Парний: Приймає -> Відправляє
        received_list = comm.recv(source=neighbor, tag=50)
        comm.send(my_list, dest=neighbor, tag=50)

    # === 3. ВИВІД РЕЗУЛЬТАТУ ===
    # Ми отримали повноцінний Python-список, з яким можна працювати далі
    print(f"SUCCESS: Process {rank} received list: {received_list} (Type: {type(received_list)})")

if __name__ == "__main__":
    main()
