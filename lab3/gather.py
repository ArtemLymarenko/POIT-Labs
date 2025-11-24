from mpi4py import MPI
import random

# кожен процес створює список із випадкових чисел
def generateRandomList(size=4):
    return [random.randint(1, 100) for _ in range(size)]

def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()
    host = MPI.Get_processor_name()

    # кожен процес створює свої дані
    random_number = random.randint(1, 50)
    random_list = generateRandomList()

    sendData = {
        "rank": rank,
        "number": random_number,
        "list": random_list
    }

    print(f"Process {rank} of {size} on {host} generated data: {sendData}")

    # збір усіх даних на root-процесі
    gathered = comm.gather(sendData, root=0)

    # root отримує повний список словників
    if rank == 0:
        print("\nGATHER RESULT ON ROOT:")
        for entry in gathered:
            print(entry)

main()
