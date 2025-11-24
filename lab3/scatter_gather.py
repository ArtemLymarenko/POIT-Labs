from mpi4py import MPI
import numpy as np

# Генерація масиву випадкових чисел
def genRandomArray(totalElements):
    return np.random.randint(1, 50, size=totalElements, dtype='u4')

# Локальна обробка елементів на кожному процесі
def localSquare(arr):
    return arr * arr   # покомпонентне піднесення до квадрату

def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()
    host = MPI.Get_processor_name()

    elementsPerProcess = 4
    totalElements = size * elementsPerProcess

    # Root створює повний масив
    if rank == 0:
        data = genRandomArray(totalElements)
        print(f"Root {rank} of {size} on {host} created array:\n{data}")
    else:
        data = None
        print(f"Worker {rank} of {size} on {host} starts with empty data")

    # Кожен процес створює локальний буфер для своєї частини
    myPart = np.empty(elementsPerProcess, dtype='u4')

    # Розсилання частин масиву
    comm.Scatter(data, myPart, root=0)
    print(f"Process {rank} received part: {myPart}")

    # Локальна робота над масивом
    processedPart = localSquare(myPart)
    print(f"Process {rank} processed part to: {processedPart}")

    # Root створює масив для збору результатів
    if rank == 0:
        result = np.empty(totalElements, dtype='u4')
    else:
        result = None

    # Збір результатів
    comm.Gather(processedPart, result, root=0)

    # Root показує результат
    if rank == 0:
        print(f"\nRoot {rank} gathered new array:\n{result}")

main()

