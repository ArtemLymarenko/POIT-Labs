import os
import numpy as np
import time

def main():
    # вимикаємо багатопотоковий BLAS
    os.environ["OMP_NUM_THREADS"] = "1"
    os.environ["OPENBLAS_NUM_THREADS"] = "1"
    os.environ["MKL_NUM_THREADS"] = "1"

    N = 6000   # 6000×6000 — оптимальний для speedup
    A = np.random.rand(N, N)
    x = np.random.rand(N)

    start = time.time()
    y = A.dot(x)
    end = time.time()

    print("Sequential MxV complete")
    print("Time:", end - start, "seconds")

if __name__ == "__main__":
    main()

