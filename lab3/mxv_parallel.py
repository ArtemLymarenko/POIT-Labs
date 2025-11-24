from mpi4py import MPI
import numpy as np
import time

def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    N = 6000
    rows_per_proc = N // size

    # Root створює матрицю і вектор
    if rank == 0:
        A = np.random.rand(N, N)
        x = np.random.rand(N)
        start = time.time()
    else:
        A = None
        x = np.empty(N, dtype='d')

    # Root розсилає вектор всім
    comm.Bcast(x, root=0)

    # Місце для локальної частини матриці
    local_A = np.empty((rows_per_proc, N), dtype='d')

    # Scatter матриці
    if rank == 0:
        # Матрицю треба передати як плаский масив
        comm.Scatter([A, rows_per_proc*N, MPI.DOUBLE], [local_A, MPI.DOUBLE], root=0)
    else:
        comm.Scatter(None, [local_A, MPI.DOUBLE], root=0)

    # Локальне множення
    local_y = local_A.dot(x)

    # Root збирає результати
    if rank == 0:
        y = np.empty(N, dtype='d')
        comm.Gather([local_y, MPI.DOUBLE], [y, MPI.DOUBLE], root=0)
        end = time.time()

        print("MPI MxV complete")
        print("Time:", end - start, "seconds")
    else:
        comm.Gather([local_y, MPI.DOUBLE], None, root=0)

if __name__ == "__main__":
    main()

