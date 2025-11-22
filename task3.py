from mpi4py import MPI
import time
import sys

def odd(number):
    if (number % 2) == 0:
        return False
    else :
        return True

def main():
    comm = MPI.COMM_WORLD
    id = comm.Get_rank()
    numProcesses = comm.Get_size()
    myHostName = MPI.Get_processor_name()

    if numProcesses < 2 or odd(numProcesses):
        if id == 0:
            print("Error: Please run with an even number of processes.")
        sys.exit(0)

    # Дані для відправки
    sendValue = id
    neighbor = id - 1 if odd(id) else id + 1

    # ==========================================
    # 1. СИНХРОННИЙ РЕЖИМ (Synchronous - ssend)
    # ==========================================
    if id == 0:
        print("\n--- MODE 1: SYNCHRONOUS (SSEND) ---")
        print("Waiting for handshake...")
    comm.Barrier() # Синхронізація перед початком етапу

    # Логіка як у вашому шаблоні: Непарні шлють, Парні приймають
    if odd(id):
        # ssend заблокується, поки neighbor не викличе recv
        comm.ssend(sendValue, dest=neighbor)
        receivedValue = comm.recv(source=neighbor)
    else:
        receivedValue = comm.recv(source=neighbor)
        comm.ssend(sendValue, dest=neighbor)

    print(f"[Sync] P{id} finished exchange.")
    comm.Barrier() # Чекаємо завершення етапу всіма процесами

    # ==========================================
    # 2. БУФЕРИЗОВАНИЙ РЕЖИМ (Buffered - bsend)
    # ==========================================
    if id == 0:
        print("\n--- MODE 2: BUFFERED (BSEND) ---")
        print("Allocating buffers...")

    # 1. Виділення та приєднання буфера
    # Розмір: дані + службова інформація MPI
    buf_size = 1024 + MPI.BSEND_OVERHEAD
    buf = bytearray(buf_size)
    MPI.Attach_buffer(buf)

    comm.Barrier()

    if odd(id):
        # bsend копіює в buf і повертається миттєво
        comm.bsend(sendValue, dest=neighbor)
        receivedValue = comm.recv(source=neighbor)
    else:
        receivedValue = comm.recv(source=neighbor)
        comm.bsend(sendValue, dest=neighbor)

    # 2. Від'єднання буфера (гарантує, що дані пішли)
    MPI.Detach_buffer()
    print(f"[Buffered] P{id} finished exchange.")
    comm.Barrier()

    # ==========================================
    # 3. РЕЖИМ ПО ГОТОВНОСТІ (Ready - rsend)
    # ==========================================
    if id == 0:
        print("\n--- MODE 3: READY (RSEND) ---")
        print("Ensuring receiver is ready before sending...")

    comm.Barrier()

    # Увага: Для rsend отримувач ОБОВ'ЯЗКОВО має вже чекати (recv).
    # Ми використовуємо time.sleep(), щоб гарантувати порядок.

    if odd(id):
        # Крок 1: Непарний відправляє
        # Чекаємо, щоб Парний точно встиг викликати recv
        time.sleep(2.0) # Було 0.2, ставимо 2.0 для надійності
        comm.rsend(sendValue, dest=neighbor)

        # Крок 2: Непарний приймає
        # Одразу стаємо на прийом, щоб Парний міг відправити нам
        receivedValue = comm.recv(source=neighbor)
    else:
        # Одразу викликаємо recv -> стаємо "Ready"
        receivedValue = comm.recv(source=neighbor)

        # Крок 2: Парний відправляє
        # Чекаємо, щоб Непарний встиг перейти до recv
        time.sleep(2.0) # Було 0.2
        comm.rsend(sendValue, dest=neighbor)


    print(f"[Ready] P{id} finished exchange.")
    comm.Barrier()

    # Фінальний вивід (як у шаблоні)
    if id == 0: print("\n--- RESULTS ---")
    comm.Barrier()
    time.sleep(0.1) # Щоб вивід не перемішався
    print(
        "Process {} of {} on {} | Final Recv: {}".format(
            id, numProcesses, myHostName, receivedValue
        )
    )

if __name__ == "__main__":
    main()
