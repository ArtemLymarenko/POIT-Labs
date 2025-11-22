from mpi4py import MPI
import numpy as np

# Функція перевірки на непарність
def odd(number):
    return number % 2 != 0

def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()
    name = MPI.Get_processor_name()

    # Перевірка, що кількість процесів парна
    if size < 2 or odd(size):
        if rank == 0:
            print("Please run this program with a positive even number of processes.")
        exit(0)

    # Підготовка даних (використовуємо numpy, як у вашому прикладі на фото)
    # rank - це число, яке ми надсилаємо
    send_data = np.array([rank], dtype='i') 
    recv_data = np.array([0], dtype='i')

    # Визначаємо сусіда
    if odd(rank):
        neighbor = rank - 1
    else:
        neighbor = rank + 1

    # === ЛОГІКА ОБМІНУ ===

    # Для простоти реалізуємо схему:
    # Непарні: ВІДПРАВЛЯЮТЬ всіма способами -> потім ПРИЙМАЮТЬ всіма способами
    # Парні:   ПРИЙМАЮТЬ всіма способами   -> потім ВІДПРАВЛЯЮТЬ всіма способами
    # Це запобігає дедлокам і дозволяє Rsend працювати коректно (бо Recv вже викликаний).

    if odd(rank):
        # --- 1. ВІДПРАВКА (Send) ---
        # Standard
        comm.Send([send_data, MPI.INT], dest=neighbor, tag=0)

        # Buffered
        buf = bytearray(MPI.BSEND_OVERHEAD + send_data.nbytes)
        MPI.Attach_buffer(buf)
        comm.Bsend([send_data, MPI.INT], dest=neighbor, tag=1)
        MPI.Detach_buffer()

        # Synchronous
        comm.Ssend([send_data, MPI.INT], dest=neighbor, tag=2)

        # Ready (працює, бо парний процес вже чекає на Recv)
        comm.Rsend([send_data, MPI.INT], dest=neighbor, tag=3)

        print(f"Process {rank} finished ALL SENDS to {neighbor}")

        # --- 2. ПРИЙОМ (Receive) ---
        comm.Recv([recv_data, MPI.INT], source=neighbor, tag=0) # Standard
        comm.Recv([recv_data, MPI.INT], source=neighbor, tag=1) # Buffered
        comm.Recv([recv_data, MPI.INT], source=neighbor, tag=2) # Sync
        comm.Recv([recv_data, MPI.INT], source=neighbor, tag=3) # Ready

        print(f"Process {rank} finished ALL RECVS from {neighbor}. Last value: {recv_data[0]}")

    else:
        # --- 1. ПРИЙОМ (Receive) ---
        # Парні процеси спочатку слухають, що робить їх готовими до Rsend від сусідів
        comm.Recv([recv_data, MPI.INT], source=neighbor, tag=0) # Standard
        comm.Recv([recv_data, MPI.INT], source=neighbor, tag=1) # Buffered
        comm.Recv([recv_data, MPI.INT], source=neighbor, tag=2) # Sync
        comm.Recv([recv_data, MPI.INT], source=neighbor, tag=3) # Ready

        print(f"Process {rank} finished ALL RECVS from {neighbor}. Last value: {recv_data[0]}")

        # --- 2. ВІДПРАВКА (Send) ---
        # Standard
        comm.Send([send_data, MPI.INT], dest=neighbor, tag=0)

        # Buffered
        buf = bytearray(MPI.BSEND_OVERHEAD + send_data.nbytes)
        MPI.Attach_buffer(buf)
        comm.Bsend([send_data, MPI.INT], dest=neighbor, tag=1)
        MPI.Detach_buffer()

        # Synchronous
        comm.Ssend([send_data, MPI.INT], dest=neighbor, tag=2)

        # Ready
        comm.Rsend([send_data, MPI.INT], dest=neighbor, tag=3)

        print(f"Process {rank} finished ALL SENDS to {neighbor}")

if __name__ == "__main__":
    main()
