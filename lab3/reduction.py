from mpi4py import MPI
import random

def sumListElementwise(a, b):
    return [x + y for x, y in zip(a, b)]

def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()
    host = MPI.Get_processor_name()

    # Кожен процес генерує випадкові числа
    value = random.randint(1, 50)
    listValue = [random.randint(0, 10) for _ in range(5)]

    print(f"Process {rank} on {host} generated number {value} and list {listValue}")

    if size > 1:
        # Стандартні редукції для скалярів
        total = comm.reduce(value, op=MPI.SUM, root=0)
        maximum = comm.reduce(value, op=MPI.MAX, root=0)
        minimum = comm.reduce(value, op=MPI.MIN, root=0)

        # Редукція списків
        listSum = comm.reduce(listValue, op=MPI.SUM, root=0)
        # Користувацька покомпонентна операція
        listElementwise = comm.reduce(listValue, op=sumListElementwise, root=0)
    else:
        total, maximum, minimum = value, value, value
        listSum = listValue
        listElementwise = listValue

    if rank == 0:
        print("\nREDUCTION RESULTS:")
        print(f"Sum of numbers:          {total}")
        print(f"Max of numbers:          {maximum}")
        print(f"Min of numbers:          {minimum}")
        print(f"Sum of lists (mpi sum):  {listSum}")
        print(f"Elementwise list sum:    {listElementwise}")

main()

