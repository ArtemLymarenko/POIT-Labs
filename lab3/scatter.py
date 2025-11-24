from mpi4py import MPI
import random

# Генерує список списків, кожен з яких піде своєму процесу
def generateListOfRandomLists(numProcesses, listSize=4):
    data = []
    for _ in range(numProcesses):
        sublist = [random.randint(1, 50) for _ in range(listSize)]
        data.append(sublist)
    return data

def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()
    host = MPI.Get_processor_name()

    # root генерує великий список списків
    if rank == 0:
        data = generateListOfRandomLists(size)
        print(f"Root {rank} of {size} on {host} generated list: {data}")
    else:
        data = None
        print(f"Worker {rank} of {size} on {host} starts with {data}")

    # кожен процес отримує один елемент списку
    result = comm.scatter(data, root=0)

    print(f"Process {rank} of {size} on {host} received: {result}")

    if rank == 0:
        print(f"Root {rank} still has original list after scatter: {data}")

main()
