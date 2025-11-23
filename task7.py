from mpi4py import MPI
import numpy as np

def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    N_VARIANT = 7               # номер варіанту
    TOTAL_ITEMS = 1000 * N_VARIANT
    MIN_VAL, MAX_VAL = 0, 100   # Діапазон чисел
    BINS = 10                   # Кількість стовпчиків гістограми

    # Розрахунок розміру шматка даних для одного процесу
    chunk_size = TOTAL_ITEMS // size

    # Змінна для локальних даних
    local_data = np.empty(chunk_size, dtype='i')

    # ЕТАП 1: РОЗСИЛКА ДАНИХ (БЛОКУЮЧИЙ ОБМІН)
    if rank == 0:
        print(f"--- START: Generating {TOTAL_ITEMS} numbers for {size} processes ---")

        # Генеруємо повний масив (тільки на Master)
        full_data = np.random.randint(MIN_VAL, MAX_VAL + 1, size=TOTAL_ITEMS, dtype='i')

        # 1. Відправляємо порції іншим процесам
        for i in range(1, size):
            # Вирізаємо шматок
            start = i * chunk_size
            end = start + chunk_size
            data_to_send = full_data[start:end]

            # Використовуємо Send (блокуючий, для буферів)
            comm.Send([data_to_send, MPI.INT], dest=i, tag=10)

        # 2. Залишаємо собі перший шматок
        local_data = full_data[0:chunk_size]
        print("[Master] Data distributed via blocking Send.")

    else:
        # Worker-и чекають на дані
        # Використовуємо Recv (блокуючий)
        comm.Recv([local_data, MPI.INT], source=0, tag=10)

    # ЕТАП 2: ЛОКАЛЬНІ ОБЧИСЛЕННЯ (ПАРАЛЕЛЬНО)
    # 1. Локальна сума
    loc_sum = np.sum(local_data)

    # 2. Локальна сума квадратів (потрібна для дисперсії)
    # Конвертуємо в int64, щоб уникнути переповнення
    loc_sq_sum = np.sum(local_data.astype(np.int64) ** 2)

    # 3. Локальна гістограма
    loc_hist, _ = np.histogram(local_data, bins=BINS, range=(MIN_VAL, MAX_VAL))

    loc_count = len(local_data)

    comm.Barrier() # Синхронізуємо всі процеси перед стартом
    start_time = MPI.Wtime()

    # ЕТАП 3: ЗБІР РЕЗУЛЬТАТІВ (ПАТЕРН: ОБМІН СПИСКАМИ ДАНИХ)
    if rank == 0:
        # Ініціалізуємо загальні змінні результатами майстра
        total_sum = loc_sum
        total_sq_sum = loc_sq_sum
        total_hist = loc_hist
        total_count = loc_count

        print("[Master] Collecting results via List exchange...")

        # У циклі приймаємо пакети від кожного Worker-а
        for i in range(1, size):
            # Використовуємо recv (мала літера) для отримання словника/списку
            result_pkg = comm.recv(source=i, tag=20)

            # Розпаковка та агрегація
            total_sum += result_pkg['s']
            total_sq_sum += result_pkg['sq']
            total_hist += result_pkg['h']
            total_count += result_pkg['c']

        # ЕТАП 4: ФІНАЛЬНА СТАТИСТИКА

        # Середнє
        mean_val = total_sum / total_count

        # Стандартне відхилення
        # Var = Mean(X^2) - (Mean(X))^2
        variance = (total_sq_sum / total_count) - (mean_val ** 2)
        std_dev = np.sqrt(variance)

        print("\n" + "="*40)
        print(f" FINAL RESULTS (N={N_VARIANT})")
        print("="*40)
        print(f"Total Elements: {total_count}")
        print(f"Mean:           {mean_val:.4f}")
        print(f"Std Deviation:  {std_dev:.4f}")
        print("-" * 40)
        print("Histogram:")
        print(total_hist)

        # Візуалізація гістограми (текстова)
        print("-" * 40)
        max_h = max(total_hist)
        for idx, val in enumerate(total_hist):
            bar_len = int((val / max_h) * 20)
            range_lbl = f"{idx*10}-{(idx+1)*10}"
            print(f"{range_lbl:7} : {'#' * bar_len} ({val})")

    else:
        # Worker пакує результати у словник (зручніше ніж просто список)
        result_pkg = {
            's': loc_sum,
            'sq': loc_sq_sum,
            'h': loc_hist,
            'c': loc_count
        }
        # Використовуємо send (мала літера) для відправки об'єкта
        comm.send(result_pkg, dest=0, tag=20)

    # КІНЕЦЬ ВИМІРУ ЧАСУ
    # ==========================================
    comm.Barrier() # Чекаємо, поки всі закінчать
    end_time = MPI.Wtime()
    if rank == 0:       
        execution_time = end_time - start_time
        print(f"Processes: {size} | Time: {execution_time:.6f} sec")

if __name__ == "__main__":
    main()
