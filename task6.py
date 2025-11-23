from mpi4py import MPI

def main():
    comm = MPI.COMM_WORLD
    id = comm.Get_rank()            # Номер поточного процесу
    numProcesses = comm.Get_size()  # Загальна кількість процесів
    myHostName = MPI.Get_processor_name()

    if numProcesses > 1:
        # --- ЛОГІКА МАЙСТРА (Початок і кінець кільця) ---
        if id == 0:
            # 1. Створюємо початковий список
            sendList = [id]

            # 2. Відправляємо першому робочому процесу (id + 1)
            comm.send(sendList, dest=id + 1)
            print(f"Master Process {id} on {myHostName} started ring with {sendList}")

            # 3. Чекаємо повернення списку від останнього процесу
            receivedList = comm.recv(source=numProcesses - 1)
            print(f"Master Process {id} on {myHostName} received final list: {receivedList}")

        # --- ЛОГІКА РОБОЧИХ ПРОЦЕСІВ (Ланки кільця) ---
        else:
            # 1. Отримуємо список від попереднього процесу (id - 1)
            receivedList = comm.recv(source=id - 1)

            # 2. Додаємо свій номер до списку
            sendList = receivedList + [id]

            # 3. Відправляємо далі по колу.
            # Формула (id + 1) % numProcesses забезпечує, що останній процес відправить 0-му.
            dest = (id + 1) % numProcesses
            comm.send(sendList, dest=dest)

            print(f"Worker Process {id} on {myHostName} received {receivedList} and sent {sendList}")

    else:
        print("Please run this program with the number of processes greater than 1")

if __name__ == "__main__":
    main()
