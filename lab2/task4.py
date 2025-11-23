from mpi4py import MPI
import time

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

    # Визначаємо сусіда
    neighbor = rank - 1 if odd(rank) else rank + 1

    send_val = rank
    print(f"[P{rank}] Initialized. Prepare to exchange with P{neighbor}")

    # === НЕБЛОКУЮЧИЙ ОБМІН ===

    # 1. Ініціалізація ПРИЙОМУ (Irecv)
    # Функція повертає об'єкт Request, але не чекає даних
    print(f"[P{rank}] Starting non-blocking Receive...")
    req_recv = comm.irecv(source=neighbor, tag=11)

    # 2. Ініціалізація ВІДПРАВКИ (Isend)
    # Функція повертає об'єкт Request і миттєво йде далі
    print(f"[P{rank}] Starting non-blocking Send ({send_val})...")
    req_send = comm.isend(send_val, dest=neighbor, tag=11)

    # 3. КОРИСНА РОБОТА (Overlapping)
    # У цей час, поки дані "летять" по мережі, процесор не простоює.
    # Ми можемо виконувати обчислення.
    print(f"[P{rank}] Doing some calculations while waiting...")
    time.sleep(1) # Імітація обчислень

    # 4. ОЧІКУВАННЯ ЗАВЕРШЕННЯ (Wait)
    # Тепер нам потрібні результати, тому ми явно чекаємо завершення.

    # Чекаємо, поки відправка точно завершиться (буфер стане вільним)
    req_send.wait()
    print(f"[P{rank}] Send completed.")

    # Чекаємо, поки дані точно прийдуть
    received_val = req_recv.wait()
    print(f"[P{rank}] Receive completed. Got data: {received_val}")

    # Фінальний вивід
    print(f"SUCCESS: Process {rank} on {name} | Sent: {send_val} | Received: {received_val}")

if __name__ == "__main__":
    main()
