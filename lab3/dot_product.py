from mpi4py import MPI
import numpy as np

def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    # Параметри задачі
    N = 500000000  # Розмір векторів (має ділитися на кількість процесів)

    # Перевірка на кратність (щоб Scatter працював коректно без зайвих ускладнень)
    if N % size != 0:
        if rank == 0:
            print(f"Error: Розмір вектора {N} не ділиться націло на {size} процесів.")
        return

    local_n = N // size  # Кількість елементів на один процес

    # 1. Ініціалізація даних (Тільки на Root)
    if rank == 0:
        # Генеруємо вектори A і B (Техніка з п. 2.5 scatter_gather.py)
        A = np.random.rand(N).astype(np.float64)
        B = np.random.rand(N).astype(np.float64)
        print(f"Root: згенеровано вектори розміром {N}")
    else:
        A = None
        B = None

    # Буфери для отримання частин векторів
    local_A = np.empty(local_n, dtype=np.float64)
    local_B = np.empty(local_n, dtype=np.float64)

    # Синхронізація перед початком заміру часу
    comm.Barrier()
    start_time = MPI.Wtime()

    # 2. Розподіл даних (Scatter) - Техніка з п. 2.1
    # Розсилаємо частини вектора A
    comm.Scatter(A, local_A, root=0)
    # Розсилаємо частини вектора B
    comm.Scatter(B, local_B, root=0)

    # 3. Локальні обчислення (Parallel Calculation)
    # Кожен процес рахує скалярний добуток своєї частини
    # local_dot = sum(a[i] * b[i])
    local_dot = np.dot(local_A, local_B)

    # 4. Збір результатів (Reduce) - Техніка з п. 2.0 (reduction.py)
    # Сумуємо всі local_dot в одну змінну global_dot на процесі 0
    global_dot = comm.reduce(local_dot, op=MPI.SUM, root=0)

    end_time = MPI.Wtime()

    # 5. Вивід результату
    if rank == 0:
        print(f"Результат (MPI): {global_dot}")
        print(f"Час виконання: {end_time - start_time:.6f} сек.")

        # Для перевірки (не для заміру часу) порахуємо послідовно
        # serial_dot = np.dot(A, B)
        # print(f"Перевірка (Serial): {serial_dot}")

if __name__ == "__main__":
    main()

