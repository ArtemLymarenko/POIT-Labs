from mpi4py import MPI

# function to return whether a number of a process is odd or even
def odd(number):
    if (number % 2) == 0:
        return False
    else :
        return True

def main():
    comm = MPI.COMM_WORLD
    id = comm.Get_rank()            #number of the process running the code"
    numProcesses = comm.Get_size()  #total number of processes running"
    myHostName = MPI.Get_processor_name()  #machine name running the code"

    # num of processes must be even
    if numProcesses > 1 and not odd(numProcesses):
        sendValue = id

         #odd processes receive from their paired 'neighbor', then send
        if odd(id):
            comm.send(sendValue, dest=id - 1)
            receivedValue = comm.recv(source=id - 1)

        #even processes receive from their paired 'neighbor', then send
        else:
            receivedValue = comm.recv(source=id + 1)
            comm.send(sendValue, dest=id + 1)

        print(
            "Process {} of {} on {} computed {} and received {}".format(
                id, numProcesses, myHostName, sendValue, receivedValue
            )
        )

    else:
        if id == 0:
            print("Please run this program with a positive even number of processes.")

if __name__ == "__main__":
    main()

