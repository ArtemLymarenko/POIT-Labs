from mpi4py import MPI
import random

def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    if size < 2:
        if rank == 0:
            print("Запустіть програму принаймні з двома процесами.")
        return

    # Лише root генерує випадковий масив
    if rank == 0:
        data = [random.randint(0, 100) for _ in range(5)]
        print(f"Root {rank} згенерував масив: {data}")
    else:
        data = None

    # Широкомовне розсилання
    data = comm.bcast(data, root=0)

    # Кожен процес виводить отриманий результат
    print(f"Процес {rank} отримав масив: {data}")

main()

